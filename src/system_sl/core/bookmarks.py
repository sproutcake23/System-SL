"""
═══════════════════════════════════════════════════════════════════
  SL - Browser Bookmark Extraction & Keyword Mining
═══════════════════════════════════════════════════════════════════
  Reads the user's browser bookmarks and writes a single structured
  snapshot to ``bookmarks.json`` in the system-sl config directory.

  Two unrelated storage formats are supported:

  * Gecko  (Zen, Firefox, LibreWolf, Waterfox, Floorp) -> places.sqlite
  * Chromium (Chrome, Chromium, Brave, Edge, Vivaldi, Opera)
    -> Bookmarks (JSON)

  These differ in more than syntax. Gecko timestamps are microseconds
  since 1970, Chromium's are microseconds since 1601, and the Gecko
  database is a live SQLite file held open by the running browser.
  Mixing up either one fails silently rather than raising, so the two
  conversions and the two readers are kept deliberately separate.

  Keyword extraction uses the spaCy ``en_core_web_md`` tagger and
  lemmatizer. spaCy is not a keyword extractor: it labels tokens, and
  the rule below selects content words from those labels. See
  ``extract_keywords`` for the rule and the reasoning behind each
  clause.

  Standalone use::

      python -m system_sl.core.bookmarks --list-profiles
      python -m system_sl.core.bookmarks --limit 20
"""

from __future__ import annotations

import argparse
import configparser
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import parse_qsl, unquote, urlparse

from system_sl.utils import get_tasks_file_path

# The two timestamp origins. Gecko counts from the Unix epoch; Chromium
# inherited the WebKit/Windows FILETIME epoch. Reading a Chromium value
# as if it were Unix lands roughly three centuries in the future with
# no error at all, which is why both names carry their browser family.
GECKO_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
WEBKIT_EPOCH = datetime(1601, 1, 1, tzinfo=timezone.utc)

# Anything decoding to before this is a placeholder or corruption rather
# than a real bookmark. Guards against a literal 0 (a common "unknown"
# sentinel) becoming 1970-01-01, and against a Gecko value misread
# through the WebKit epoch becoming 1601-01-01.
MIN_PLAUSIBLE_YEAR = 1990

# Gecko stores its internal root folder names in English in the database
# rather than localizing them, so they can be mapped to display names.
GECKO_ROOT_FOLDERS = {
    "menu": "Bookmarks Menu",
    "toolbar": "Bookmarks Toolbar",
    "unfiled": "Other Bookmarks",
    "mobile": "Mobile Bookmarks",
    "tags": "Tags",
}

# URL fragments that carry no topical meaning. Dropping them keeps the
# slug usable as a keyword source instead of drowning it in boilerplate.
URL_NOISE = frozenset(
    {
        "www", "www2", "m1", "m", "web", "com", "org", "net", "edu", "gov", "io", "co",
        "uk", "de", "fr", "in", "us", "html", "htm", "php", "aspx", "jsp", "xml",
        "index", "default", "en", "en-us", "amp", "http", "https", "www1",
        "utm", "ref", "referrer", "source", "share", "shareid", "gclid", "fbclid",
        "feature", "si", "t", "s", "q", "hl", "lang", "locale", "search",
    }
)

# Query parameters that exist to attribute a visit, not to describe a
# page. They are dropped by key rather than by token: splitting
# "?utm_source=firefox-browser" on punctuation yields the harmless-looking
# words "utm", "firefox" and "browser", which would otherwise be mined as
# real keywords and land in the top-keyword list.
TRACKING_PREFIXES = ("utm_", "mc_", "_hs", "pk_", "mtm_", "oly_", "vero_")
TRACKING_KEYS = frozenset(
    {
        "gclid", "fbclid", "dclid", "msclkid", "yclid", "igshid", "spm", "mkt_tok",
        "ref", "referrer", "source", "share", "shareid", "si", "_ga", "_gl", "at_medium",
    }
)

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.\w+")
URL_SPLIT_RE = re.compile(r"[^A-Za-z0-9]+")

KEEP_POS = frozenset({"NOUN", "PROPN", "ADJ"})
MIN_LEMMA_LENGTH = 3
MAX_KEYWORDS = 8
MAX_PHRASES = 4

# Chunks are only useful when they are short, fully alphabetic and free
# of determiners. Unfiltered, ``noun_chunks`` yields things like
# "github - probonopd" and "- user@gmail.com - gmail".
PHRASE_DROP_POS = frozenset({"DET", "PRON", "ADP", "PUNCT", "SYM", "PART", "NUM", "CCONJ", "SCONJ"})


# =====================================================================
# 1. PROFILE DISCOVERY
# =====================================================================


@dataclass
class Profile:
    """A single browser profile that may hold bookmarks."""

    family: str  # "gecko" | "chromium"
    browser: str  # "zen", "firefox", "chrome", "brave", ...
    name: str  # profile name, e.g. "Default (release)" or "Default"
    directory: Path
    data_file: Path  # places.sqlite for gecko, Bookmarks for chromium
    is_default: bool = False

    @property
    def label(self) -> str:
        return f"{self.browser} / {self.name}"


def _gecko_roots() -> List[Path]:
    """Candidate Gecko installation directories, per platform.

    Gecko browsers keep profiles under a per-family directory, so every
    root here is the directory that contains ``profiles.ini``.
    """
    home = Path.home()

    if os.name == "nt":
        # Gecko uses roaming AppData; Chromium uses Local. See
        # _chromium_user_data_dirs.
        appdata = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
        return [appdata / "zen", appdata / "Mozilla" / "Firefox"]

    if sys.platform == "darwin":
        base = home / "Library" / "Application Support"
        return [base / "zen", base / "Firefox"]

    xdg = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
    return [
        xdg / "zen",
        home / ".mozilla" / "firefox",
        home / "snap" / "firefox" / "common" / ".mozilla" / "firefox",
        home / ".var" / "app" / "app.zen_browser.zen" / "config" / "zen",
        home / ".var" / "app" / "org.mozilla.firefox" / ".mozilla" / "firefox",
    ]


def _chromium_user_data_dirs() -> List[tuple]:
    """Candidate Chromium user-data directories as ``(browser, path)``.

    This is the directory that contains per-profile subdirectories such
    as ``Default`` and ``Profile 1``. Opera is the exception: it keeps
    ``Bookmarks`` directly in this directory, which the scanner handles
    by considering the directory itself as well as its children.
    """
    home = Path.home()

    if os.name == "nt":
        local = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
        roaming = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
        return [
            ("chrome", local / "Google" / "Chrome"),
            ("chromium", local / "Chromium"),
            ("brave", local / "BraveSoftware" / "Brave-Browser"),
            ("edge", local / "Microsoft" / "Edge"),
            ("vivaldi", local / "Vivaldi"),
            ("opera", roaming / "Opera Software" / "Opera Stable"),
            ("opera-gx", roaming / "Opera Software" / "Opera GX Stable"),
        ]

    if sys.platform == "darwin":
        base = home / "Library" / "Application Support"
        return [
            ("chrome", base / "Google" / "Chrome"),
            ("chromium", base / "Chromium"),
            ("brave", base / "BraveSoftware" / "Brave-Browser"),
            ("edge", base / "Microsoft Edge"),
            ("vivaldi", base / "Vivaldi"),
            ("opera", base / "com.operasoftware.Opera"),
            ("opera-gx", base / "com.operasoftware.OperaGX"),
        ]

    xdg = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
    relative = [
        ("chrome", "google-chrome"),
        ("chromium", "chromium"),
        ("brave", "BraveSoftware/Brave-Browser"),
        ("edge", "microsoft-edge"),
        ("vivaldi", "vivaldi"),
        ("opera", "opera"),
        ("opera-gx", "opera-gx"),
    ]

    found = [(browser, xdg / path) for browser, path in relative]
    found.append(("chromium", home / "snap" / "chromium" / "common" / "chromium"))

    # Flatpak ships each browser under its own application id.
    flatpak = [
        ("com.google.Chrome", "chrome", "google-chrome"),
        ("org.chromium.Chromium", "chromium", "chromium"),
        ("com.brave.Browser", "brave", "BraveSoftware/Brave-Browser"),
        ("com.microsoft.Edge", "edge", "microsoft-edge"),
        ("com.vivaldi.Vivaldi", "vivaldi", "vivaldi"),
        ("com.operasoftware.Opera", "opera", "opera"),
        ("com.operasoftware.OperaGX", "opera-gx", "opera-gx"),
    ]
    for app_id, browser, path in flatpak:
        found.append((browser, home / ".var" / "app" / app_id / "config" / path))

    return found


def _read_toolkit_ini(path: Path) -> configparser.ConfigParser:
    """Read a Firefox Toolkit ini file verbatim.

    Interpolation is disabled because profile paths legitimately contain
    ``%`` on Windows, which the default parser would try to expand.
    """
    ini = configparser.ConfigParser(interpolation=None)
    ini.read(path, encoding="utf-8")
    return ini


def _looks_like_sqlite(path: Path) -> bool:
    """Whether ``path`` is a non-empty SQLite database.

    Discovery deliberately does not open the file. Opening a live
    ``places.sqlite`` fails with "database is locked" while the browser
    is running, and a size plus magic check is enough to reject the
    traps that actually occur -- notably a zero-byte ``places.sqlite``
    left behind by an abandoned profile.
    """
    try:
        if not path.is_file() or path.stat().st_size < 100:
            return False
        with path.open("rb") as handle:
            return handle.read(16) == b"SQLite format 3\x00"
    except OSError:
        return False


def _discover_gecko_profiles(default_only: bool) -> List[Profile]:
    """Find Gecko profiles that hold a usable bookmark database.

    Precedence per root follows Firefox's own rules: the ``Default``
    entry in ``installs.ini`` wins, then the ``Profile`` section marked
    ``Default=1`` in ``profiles.ini``, then the first *valid* candidate.
    Validity is checked rather than assumed, because a profile directory
    can exist and be marked default while its database is empty.
    """
    profiles: List[Profile] = []

    for root in _gecko_roots():
        if not root.is_dir():
            continue

        for profiles_ini in sorted(root.rglob("profiles.ini")):
            base = profiles_ini.parent
            ini = _read_toolkit_ini(profiles_ini)

            candidates: List[tuple] = []
            for section in ini.sections():
                if not section.startswith("Profile"):
                    continue
                raw_path = ini[section].get("Path")
                if not raw_path:
                    continue
                directory = Path(raw_path).expanduser()
                if ini[section].get("IsRelative", "1") == "1":
                    directory = base / directory
                if not directory.is_dir():
                    continue
                if not _looks_like_sqlite(directory / "places.sqlite"):
                    continue
                marked_default = ini[section].get("Default", "").lower() in {"1", "true"}
                candidates.append((marked_default, section, directory))

            if not candidates:
                continue

            browser = root.name.lower()

            ordered: List[tuple] = []
            # installs.ini names the default by directory, while the
            # friendly label lives in profiles.ini, so carry it across.
            labels = {
                str(directory): ini[section].get("Name", section)
                for _, section, directory in candidates
            }

            installs_ini = profiles_ini.with_name("installs.ini")
            if installs_ini.is_file():
                installs = _read_toolkit_ini(installs_ini)
                for section in installs.sections():
                    default = installs[section].get("Default")
                    if not default:
                        continue
                    directory = (base / default).resolve()
                    if not _looks_like_sqlite(directory / "places.sqlite"):
                        continue
                    ordered.append(
                        (True, labels.get(str(directory), directory.name), directory)
                    )

            for marked_default, section, directory in candidates:
                if marked_default:
                    ordered.append((True, ini[section].get("Name", section), directory))

            for _, section, directory in candidates:
                ordered.append((False, ini[section].get("Name", section), directory))

            seen: set = set()
            for is_default, name, directory in ordered:
                key = str(directory)
                if key in seen:
                    continue
                seen.add(key)
                profiles.append(
                    Profile(
                        family="gecko",
                        browser=browser,
                        name=name,
                        directory=directory,
                        data_file=directory / "places.sqlite",
                        is_default=is_default,
                    )
                )
                if default_only:
                    break

    return profiles


def _discover_chromium_profiles(default_only: bool) -> List[Profile]:
    """Find Chromium profiles holding a ``Bookmarks`` file.

    Every profile directory is considered, not just ``Default``, because
    Chromium happily keeps bookmarks in ``Profile 1`` and friends. The
    user-data directory itself is included so that Opera's flat layout is
    covered by the same code path.
    """
    profiles: List[Profile] = []

    for browser, user_data in _chromium_user_data_dirs():
        if not user_data.is_dir():
            continue

        try:
            subdirectories = sorted(
                (entry for entry in user_data.iterdir() if entry.is_dir()),
                key=lambda entry: (entry.name != "Default", entry.name),
            )
        except OSError:
            subdirectories = []

        for directory in [user_data] + subdirectories:
            bookmarks_file = directory / "Bookmarks"
            fallback = directory / "Bookmarks.bak"
            if not bookmarks_file.is_file() and not fallback.is_file():
                continue

            # Named after the directory, so Opera's flat layout reads as
            # "opera" rather than the misleading "Default".
            name = directory.name
            profiles.append(
                Profile(
                    family="chromium",
                    browser=browser,
                    name=name,
                    directory=directory,
                    data_file=bookmarks_file if bookmarks_file.is_file() else fallback,
                    is_default=(name == "Default"),
                )
            )
            if default_only:
                break

    return profiles


def find_profiles(
    default_only: bool = False, browsers: Optional[Sequence[str]] = None
) -> List[Profile]:
    """Discover every readable browser profile holding bookmarks.

    Args:
        default_only: Restrict to each browser's primary profile.
        browsers: Optional filter accepting browser ids ("zen", "brave")
            or family names ("gecko", "chromium").

    Returns:
        List[Profile]: Discovered profiles, Gecko first.
    """
    profiles = _discover_gecko_profiles(default_only) + _discover_chromium_profiles(default_only)

    if browsers:
        wanted = {name.strip().lower() for name in browsers if name.strip()}
        profiles = [
            profile
            for profile in profiles
            if profile.browser.lower() in wanted or profile.family in wanted
        ]

    return profiles


# =====================================================================
# 2. TIMESTAMP CONVERSION
# =====================================================================


def _isoformat(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def gecko_timestamp_to_iso(value: Any) -> Optional[str]:
    """Convert a Gecko PRTime value (microseconds since 1970) to ISO 8601.

    A zero or absent value means the browser never recorded a time, which
    is common for imported and synced entries. Returning ``None`` keeps
    that distinguishable from an actual moment.
    """
    try:
        micros = int(value)
    except (TypeError, ValueError):
        return None
    if micros <= 0:
        return None

    moment = GECKO_EPOCH + timedelta(microseconds=micros)
    if moment.year < MIN_PLAUSIBLE_YEAR or moment > datetime.now(timezone.utc) + timedelta(days=1):
        return None
    return _isoformat(moment)


def webkit_timestamp_to_iso(value: Any) -> Optional[str]:
    """Convert a Chromium timestamp (microseconds since 1601) to ISO 8601.

    Chromium stores ``date_added`` and ``date_last_used`` as strings, and
    uses ``"0"`` for entries it never stamped. Applying the Gecko
    conversion here would not raise -- it would simply report a date
    centuries in the future.
    """
    try:
        micros = int(value)
    except (TypeError, ValueError):
        return None
    if micros <= 0:
        return None

    moment = WEBKIT_EPOCH + timedelta(microseconds=micros)
    if moment.year < MIN_PLAUSIBLE_YEAR or moment > datetime.now(timezone.utc) + timedelta(days=1):
        return None
    return _isoformat(moment)


# =====================================================================
# 3. TEXT PREPARATION
# =====================================================================


def strip_boilerplate(title: str, url: str) -> str:
    """Remove the parts of a title the URL already tells us.

    Two high-precision edits: drop e-mail addresses, and drop a *trailing*
    site-name segment such as ``" · GitHub"`` or ``" | YouTube"``.

    Only trailing segments are removed. A leading one is not safe: the
    title ``"cliamp — terminal music player"`` names the product in the
    hostname, so stripping any hostname match would delete the single
    most important keyword.
    """
    cleaned = EMAIL_RE.sub(" ", title or "")

    host = urlparse(url or "").netloc.split("@")[-1].split(":")[0]
    labels = host.split(".")
    site = labels[-2] if len(labels) >= 2 else labels[0] if labels else ""
    if len(site) >= 3:
        cleaned = re.sub(
            rf"\s*[-–—|·:]\s*{re.escape(site)}\s*$", "", cleaned, flags=re.IGNORECASE
        )

    cleaned = " ".join(cleaned.split())
    # Never let cleanup destroy the title outright.
    return cleaned or " ".join((title or "").split())


def slug_tokens(url: str) -> List[str]:
    """Topical word tokens extracted from a URL.

    Scheme, hostname suffixes, tracking parameters, digits and file
    extensions are dropped. What survives is the kind of word a title
    often omits, e.g. ``asyncio task`` from a documentation URL.
    """
    parsed = urlparse(url or "")
    host = parsed.netloc.split("@")[-1].split(":")[0]
    labels = host.split(".")
    if len(labels) > 1:
        labels = labels[:-1]

    chunks = list(labels)
    chunks.append(unquote(parsed.path))

    for key, value in parse_qsl(parsed.query, keep_blank_values=False):
        lowered = key.lower()
        if lowered.startswith(TRACKING_PREFIXES) or lowered in TRACKING_KEYS:
            continue
        chunks.append(f"{key} {value}")

    raw = " ".join(chunks)

    tokens: List[str] = []
    for token in URL_SPLIT_RE.split(raw):
        lowered = token.lower()
        if len(token) < 2 or token.isdigit() or lowered in URL_NOISE:
            continue
        tokens.append(token)
    return tokens


def build_keyword_source(title: str, url: str) -> str:
    """Assemble the text fed to spaCy for one bookmark.

    Title first, slug second, separated by a sentence break. The break
    matters beyond readability: noun chunks are bounded by sentence, so
    without it the last word of the title fuses with the first slug token
    and phrases like "terminal gptme" appear. Keywords are unaffected --
    the added period is punctuation and the POS filter discards it.

    Order is deliberate. Keywords are capped and kept in first-seen
    order, so URL tokens can only fill leftover slots and can never
    displace a word the title already provided.
    """
    parts: List[str] = []
    cleaned = strip_boilerplate(title, url)
    if cleaned:
        parts.append(cleaned)

    tokens = slug_tokens(url)
    if tokens:
        parts.append(" ".join(tokens))

    return ". ".join(parts)


# =====================================================================
# 4. KEYWORD EXTRACTION
# =====================================================================


def dedupe_key(keyword: str) -> str:
    """Normalize a keyword for deduplication purposes only.

    Lemmatization merges inflection, but only where the tagger agrees on
    the part of speech. A title-cased word is tagged PROPN, and a PROPN
    lemma is the surface form, so "Keywords" reaches this point as
    ``keywords`` while the same word in a URL slug arrives as ``keyword``
    -- one concept, two entries.

    Stripping a trailing plural "s" collapses that pair. The guard skips
    endings where an "s" is not a plural ("class", "status", "analysis"),
    and the stored keyword is never modified, so nothing is lost if the
    heuristic declines to merge.
    """
    if (
        len(keyword) >= 4
        and keyword.endswith("s")
        and not keyword.endswith(("ss", "us", "is", "os"))
    ):
        return keyword[:-1]
    return keyword


def extract_keywords(doc: Any, limit: int = MAX_KEYWORDS) -> List[str]:
    """Select keywords from a spaCy document by part of speech and lemma.

    spaCy provides labelled tokens, not keywords; this is the rule that
    turns one into the other. Each clause removes a different kind of
    noise:

    1. ``pos_`` in NOUN/PROPN/ADJ keeps content words. PROPN matters
       because product and organisation names live there, and ADJ
       matters because words like "terminal" are tagged JJ rather than
       NOUN.
    2. ``is_stop`` drops function words that survive the POS filter.
    3. ``is_alpha`` drops digits, punctuation and e-mail fragments.
    4. The length floor drops single letters, except for all-caps
       acronyms -- "AI" is two characters and entirely meaningful.
    5. Lemmas, not surface forms, so "tools" and "tool" collapse, and
       first-seen order keeps title words ahead of URL words.

    Note that lemmatization merges inflection only: "tools" becomes
    "tool", but "document" and "documentation" remain distinct keywords.
    """
    keywords: List[str] = []
    seen: set = set()

    for token in doc:
        if token.pos_ not in KEEP_POS:
            continue
        if token.is_stop or not token.is_alpha:
            continue

        lemma = token.lemma_.lower()
        if len(lemma) < MIN_LEMMA_LENGTH and not token.is_upper:
            continue

        key = dedupe_key(lemma)
        if key in seen:
            continue

        seen.add(key)
        keywords.append(lemma)

        if len(keywords) >= limit:
            break

    return keywords


def extract_phrases(doc: Any, limit: int = MAX_PHRASES) -> List[str]:
    """Extract short noun phrases, filtered down to the useful ones.

    Raw ``noun_chunks`` are too noisy to store unfiltered: they include
    "github - probonopd" and "every repo". Constraining chunks to two or
    three fully alphabetic content words and dropping determiners keeps
    "terminal music player" and "ai agent" while discarding the rest.
    """
    phrases: List[str] = []
    seen: set = set()

    for chunk in doc.noun_chunks:
        tokens = [
            token
            for token in chunk
            if not token.is_stop and token.pos_ not in PHRASE_DROP_POS
        ]
        if not 2 <= len(tokens) <= 3:
            continue
        if not all(token.is_alpha and len(token.text) >= 2 for token in tokens):
            continue

        phrase = " ".join(token.text.lower() for token in tokens)
        if phrase in seen:
            continue

        seen.add(phrase)
        phrases.append(phrase)

        if len(phrases) >= limit:
            break

    return phrases


def _load_nlp() -> Any:
    """Load the shared spaCy model used by the ranking pipeline.

    Reusing :class:`Setup` means one ``spacy.load`` per process rather
    than one per profile, and inherits its PyInstaller bundle handling.
    """
    from system_sl.core.vector_converter import Setup

    return Setup()._get_model()


def annotate(records: List[Dict[str, Any]], use_keywords: bool = True) -> None:
    """Attach ``keywords`` and ``phrases`` to bookmark records in place.

    The whole corpus goes through ``nlp.pipe`` in one batch. ``n_process``
    stays at 1 deliberately: forking worker processes is a known source
    of failures inside a frozen AppImage build, and short strings are
    fast enough single-threaded.
    """
    for record in records:
        record["keywords"] = []
        record["phrases"] = []

    if not use_keywords or not records:
        return

    nlp = _load_nlp()
    texts = [record["_source_text"] for record in records]

    # NER is the slowest component and contributes nothing here.
    with nlp.select_pipes(disable=["ner"]):
        docs = list(nlp.pipe(texts, batch_size=64, n_process=1))

    for record, doc in zip(records, docs):
        record["keywords"] = extract_keywords(doc)
        record["phrases"] = extract_phrases(doc)


# =====================================================================
# 5. READERS
# =====================================================================


def _snapshot(database: Path) -> Path:
    """Copy a database and its write-ahead log into a temporary folder.

    A running Firefox or Zen holds ``places.sqlite`` open and leaves its
    recent writes in the ``-wal`` file. Opening the original read-only
    still fails with "database is locked", so the fix is to copy the
    file plus its sidecars and read the copy. This also guarantees the
    browser's own data is never opened for writing.
    """
    temporary = Path(tempfile.mkdtemp(prefix="system-sl-bookmarks-"))
    for suffix in ("", "-wal", "-shm"):
        source = Path(str(database) + suffix)
        if source.is_file():
            try:
                shutil.copyfile(source, temporary / (database.name + suffix))
            except OSError:
                pass
    return temporary


def _gecko_folder_paths(connection: sqlite3.Connection) -> Dict[int, str]:
    """Map every Gecko bookmark id to its human-readable folder path.

    Every node is keyed, including leaves, because the chain is walked
    recursively. A caller looking for the folder a bookmark lives in must
    therefore ask for the bookmark's ``parent`` id, not its own -- the
    leaf's own entry is its parent's path with its own title appended.
    """
    parents: Dict[int, tuple] = {}
    for row in connection.execute("SELECT id, parent, title, type FROM moz_bookmarks"):
        parents[row[0]] = (row[1], row[2], row[3])

    resolved: Dict[int, str] = {}

    def resolve(node_id: int) -> str:
        if node_id in resolved:
            return resolved[node_id]
        entry = parents.get(node_id)
        if not entry:
            return ""
        parent_id, title, _ = entry
        if parent_id in (None, 0):
            resolved[node_id] = ""
            return ""

        name = (title or "").strip()
        name = GECKO_ROOT_FOLDERS.get(name.lower(), name)
        ancestor = resolve(parent_id)
        path = f"{ancestor}/{name}".strip("/") if name else ancestor
        resolved[node_id] = path
        return path

    return {node_id: resolve(node_id) for node_id in parents}


def read_gecko_bookmarks(profile: Profile) -> List[Dict[str, Any]]:
    """Read bookmarks from a Gecko ``places.sqlite`` snapshot."""
    temporary = _snapshot(profile.data_file)
    try:
        connection = sqlite3.connect(temporary / profile.data_file.name)
        connection.row_factory = sqlite3.Row
        try:
            folders = _gecko_folder_paths(connection)
            rows = connection.execute(
                """
                SELECT b.guid AS guid, b.title AS title, p.url AS url,
                       b.dateAdded AS added, b.lastModified AS modified,
                       p.last_visit_date AS last_visit, p.visit_count AS visits,
                       p.frecency AS frecency, b.parent AS parent
                FROM moz_bookmarks AS b
                JOIN moz_places AS p ON p.id = b.fk
                WHERE b.type = 1 AND p.url IS NOT NULL AND p.hidden = 0
                ORDER BY b.dateAdded DESC
                """
            ).fetchall()
        finally:
            connection.close()
    finally:
        shutil.rmtree(temporary, ignore_errors=True)

    records: List[Dict[str, Any]] = []
    for row in rows:
        records.append(
            {
                "id": f"gecko:{profile.browser}:{row['guid']}",
                "guid": row["guid"],
                "title": row["title"] or "",
                "url": row["url"],
                "folder": folders.get(row["parent"]) or None,
                "added_utc": gecko_timestamp_to_iso(row["added"]),
                "modified_utc": gecko_timestamp_to_iso(row["modified"]),
                "last_visit_utc": gecko_timestamp_to_iso(row["last_visit"]),
                "visit_count": row["visits"],
                "frecency": row["frecency"],
            }
        )
    return records


def _walk_chromium(node: Dict[str, Any], folders: List[str], out: List[Dict[str, Any]]) -> None:
    """Depth-first walk of a Chromium bookmark tree."""
    if node.get("type") == "url":
        url = node.get("url") or ""
        if not url:
            return
        out.append(
            {
                "id": f"chromium:{node.get('guid') or node.get('id') or url}",
                "guid": node.get("guid") or node.get("id"),
                "title": node.get("name") or "",
                "url": url,
                "folder": "/".join(folders) or None,
                "added_utc": webkit_timestamp_to_iso(node.get("date_added")),
                "modified_utc": None,
                "last_visit_utc": webkit_timestamp_to_iso(node.get("date_last_used")),
                "visit_count": None,
                "frecency": None,
            }
        )
        return

    name = (node.get("name") or "").strip()
    child_folders = folders + ([name] if name else [])
    for child in node.get("children") or []:
        if isinstance(child, dict):
            _walk_chromium(child, child_folders, out)


def read_chromium_bookmarks(profile: Profile) -> List[Dict[str, Any]]:
    """Read bookmarks from a Chromium ``Bookmarks`` JSON file."""
    temporary = _snapshot(profile.data_file)
    try:
        payload = json.loads((temporary / profile.data_file.name).read_text(encoding="utf-8"))
    finally:
        shutil.rmtree(temporary, ignore_errors=True)

    records: List[Dict[str, Any]] = []
    roots = payload.get("roots") or {}
    # bookmark_bar, other and synced each hold real bookmarks; synced is
    # where bookmarks from a signed-in phone land.
    for key in ("bookmark_bar", "other", "synced", "managed"):
        root = roots.get(key)
        if isinstance(root, dict):
            _walk_chromium(root, [], records)
    return records


# =====================================================================
# 6. ORCHESTRATION
# =====================================================================


def _deduplicate(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Drop repeated URLs within one profile, keeping the newest entry.

    Sorting an absent timestamp as the empty string puts dated rows ahead
    of undated ones, so a bookmark with a real ``dateAdded`` wins over a
    synced duplicate whose timestamp the browser never recorded.
    """
    ordered = sorted(records, key=lambda row: row.get("added_utc") or "", reverse=True)

    seen: set = set()
    unique: List[Dict[str, Any]] = []
    for record in ordered:
        key = record["url"]
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique


def mine_bookmarks(
    profiles: Sequence[Profile],
    days: Optional[int] = None,
    limit: Optional[int] = None,
    use_keywords: bool = True,
) -> Dict[str, Any]:
    """Read every profile and build the snapshot document.

    A profile that cannot be read is reported in ``sources`` with its
    error rather than aborting the run: one locked or half-installed
    browser must not prevent the others from being exported.
    """
    bookmarks: List[Dict[str, Any]] = []
    sources: List[Dict[str, Any]] = []

    for profile in profiles:
        entry: Dict[str, Any] = {
            "family": profile.family,
            "browser": profile.browser,
            "profile": profile.name,
            "is_default": profile.is_default,
            "path": str(profile.data_file),
            "found": 0,
            "kept": 0,
            "skipped": 0,
            "error": None,
        }

        try:
            reader = read_gecko_bookmarks if profile.family == "gecko" else read_chromium_bookmarks
            records = _deduplicate(reader(profile))
        except Exception as error:  # noqa: BLE001 - reported, never raised
            entry["error"] = f"{type(error).__name__}: {error}"
            sources.append(entry)
            continue

        entry["found"] = len(records)

        for record in records:
            record["browser"] = profile.browser
            record["family"] = profile.family
            record["profile"] = profile.name
            record["title"] = (record.get("title") or "").strip()
            # Kept alongside the raw title so keyword output stays
            # auditable: it is the exact text spaCy was given.
            record["title_clean"] = strip_boilerplate(record["title"], record["url"])
            record["_source_text"] = build_keyword_source(record["title"], record["url"])

        annotate(records, use_keywords=use_keywords)

        kept: List[Dict[str, Any]] = []
        for record in records:
            # A row with nothing to say is noise, not data. In practice
            # this gate fires rarely, because the URL usually contributes
            # a word even when the title is empty; it exists to stop an
            # empty keyword list from entering the snapshot.
            if use_keywords and not record["keywords"]:
                entry["skipped"] += 1
                continue
            kept.append(record)

        entry["kept"] = len(kept)
        sources.append(entry)
        bookmarks.extend(kept)

    unknown_added = sum(1 for record in bookmarks if not record.get("added_utc"))

    if days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        bookmarks = [
            record
            for record in bookmarks
            if record.get("added_utc") and datetime.fromisoformat(record["added_utc"]) >= cutoff
        ]

    # Newest first, with undated entries last. This ordering is what
    # makes "--limit N" mean "the N most recently added bookmarks".
    bookmarks.sort(key=lambda row: row.get("added_utc") or "", reverse=True)

    if limit is not None and limit > 0:
        bookmarks = bookmarks[:limit]

    for record in bookmarks:
        record.pop("_source_text", None)

    counter: Dict[str, int] = {}
    for record in bookmarks:
        for keyword in record["keywords"]:
            counter[keyword] = counter.get(keyword, 0) + 1
    top_keywords = [
        {"keyword": keyword, "count": count}
        for keyword, count in sorted(counter.items(), key=lambda pair: (-pair[1], pair[0]))
    ]

    spacy_info: Dict[str, Any] = {"model": None, "version": None}
    if use_keywords:
        try:
            import spacy
            from spacy.util import get_package_version

            spacy_info = {
                "model": "en_core_web_md",
                "version": get_package_version("en_core_web_md"),
                "spacy_version": spacy.__version__,
            }
        except Exception:  # noqa: BLE001 - informational only
            pass

    return {
        "version": "1.0",
        "extracted_at": _isoformat(datetime.now(timezone.utc)),
        "spacy": spacy_info,
        "sources": sources,
        "counts": {
            "total_found": sum(source["found"] for source in sources),
            "total_kept": len(bookmarks),
            "skipped_no_keywords": sum(source["skipped"] for source in sources),
            "unknown_added": unknown_added,
            "browsers": sorted({source["browser"] for source in sources}),
        },
        "bookmarks": bookmarks,
        "top_keywords": top_keywords,
    }


def write_document(document: Dict[str, Any], destination: Optional[str] = None) -> Path:
    """Write the snapshot atomically so a crash cannot truncate it."""
    path = Path(destination) if destination else Path(get_tasks_file_path("bookmarks.json"))
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(document, handle, indent=2, ensure_ascii=False)
    os.replace(temporary, path)
    return path


# =====================================================================
# 7. COMMAND LINE
# =====================================================================


def _print_profiles(profiles: Sequence[Profile]) -> None:
    print("\n" + "═" * 68)
    print("  DISCOVERED BROWSER PROFILES")
    print("═" * 68)

    if not profiles:
        print("\n  No browser profiles with bookmarks were found.\n")
        return

    for profile in profiles:
        marker = "★" if profile.is_default else " "
        print(f"\n  {marker} {profile.label:<34} [{profile.family}]")
        print(f"      {profile.data_file}")

    found = {browser for browser, _ in _chromium_user_data_dirs()}
    listed = {profile.browser for profile in profiles}
    missing = sorted(browser for browser in found if browser not in listed)
    if missing:
        print(f"\n  Not found or no profile yet: {', '.join(missing)}")
    print()


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m system_sl.core.bookmarks",
        description="Extract browser bookmarks and mine their keywords with spaCy.",
        epilog=(
            "Filters such as --browser, --profile, --days and --limit narrow what is "
            "written, not just what is shown, so a filtered run replaces the snapshot. "
            "Use --dry-run to inspect the effect first."
        ),
    )
    parser.add_argument("--list-profiles", action="store_true", help="Only list detected browser profiles.")
    parser.add_argument("--browser", help="Comma-separated browsers or families, e.g. zen,brave or gecko.")
    parser.add_argument("--profile", help="Only profiles whose name contains this text.")
    parser.add_argument("--default-only", action="store_true", help="Restrict to each browser's primary profile.")
    parser.add_argument("--days", type=int, help="Only keep bookmarks added in the last N days.")
    parser.add_argument("--limit", type=int, help="Keep only the N most recently added bookmarks.")
    parser.add_argument("--output", help="Destination path (default: bookmarks.json in the config directory).")
    parser.add_argument("--no-keywords", action="store_true", help="Skip spaCy entirely; export bookmark metadata only.")
    parser.add_argument("--dry-run", action="store_true", help="Report what would be written without writing it.")
    parser.add_argument("--print-json", action="store_true", help="Print the document to stdout.")
    args = parser.parse_args(argv)

    browsers = args.browser.split(",") if args.browser else None
    profiles = find_profiles(default_only=args.default_only, browsers=browsers)
    if args.profile:
        needle = args.profile.lower()
        profiles = [profile for profile in profiles if needle in profile.name.lower()]

    if args.list_profiles:
        _print_profiles(profiles)
        return 0

    if not profiles:
        print("\n  No browser profiles with bookmarks were found.")
        print("  Use --list-profiles to see what was detected.\n")
        return 1

    document = mine_bookmarks(
        profiles,
        days=args.days,
        limit=args.limit,
        use_keywords=not args.no_keywords,
    )

    print("\n" + "═" * 68)
    print("  BOOKMARK EXTRACTION")
    print("═" * 68)

    for source in document["sources"]:
        if source["error"]:
            print(f"\n  ✗ {source['browser']} / {source['profile']}")
            print(f"      {source['error']}")
        else:
            print(
                f"\n  ✓ {source['browser']} / {source['profile']} "
                f"[{source['family']}]  found={source['found']} "
                f"kept={source['kept']} skipped={source['skipped']}"
            )
            print(f"      {source['path']}")

    counts = document["counts"]
    print(f"\n  Bookmarks kept    : {counts['total_kept']}")
    print(f"  Skipped (no words): {counts['skipped_no_keywords']}")
    print(f"  Unknown timestamp : {counts['unknown_added']}")

    if document["top_keywords"]:
        top = ", ".join(
            f"{entry['keyword']}({entry['count']})" for entry in document["top_keywords"][:15]
        )
        print(f"\n  Top keywords: {top}")

    if args.print_json:
        print()
        print(json.dumps(document, indent=2, ensure_ascii=False))

    if args.dry_run:
        print("\n  Dry run — nothing written.\n")
        return 0

    path = write_document(document, args.output)
    print(f"\n  Written to: {path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
