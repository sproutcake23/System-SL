"""Task prioritization engine and reorder-feedback capture.

Pure logic, no UI. The GUI calls :func:`prioritize_tasks` to render tasks in a
ranked order, and :func:`record_reorder_feedback` to capture the user's manual
re-ranking (see ``priori.jpeg``).
"""

from datetime import datetime

from system_sl.core.tasks import load_tasks, get_tasks_file_path, load_data


# Scoring weights. Tunable — these only affect the *initial* ordering the user
# sees; they drag-reorder from there and that feedback is captured separately.
OVERDUE_SCORE = 100.0   # past-due tasks float to the very top
SOON_BASE = 50.0        # a task due today scores this; further out scores less
SOON_HORIZON = 50       # days beyond which "soon" no longer adds urgency
KEYWORD_BOOST = 10.0    # title matches a persona/goal keyword


def _parse_deadline(value):
    """Parse a deadline string into a ``datetime``, or ``None`` if absent/bad.

    Accepts the two formats the app produces: ``"YYYY-MM-DD"`` (GUI add /
    Google all-day events) and ``"YYYY-MM-DD HH:MM"`` (calendar/tasks sync).
    """
    if not value or not isinstance(value, str):
        return None
    value = value.strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _deadline_score(deadline, now):
    dt = _parse_deadline(deadline)
    if dt is None:
        return 0.0
    days = (dt.date() - now.date()).days
    if days < 0:
        return OVERDUE_SCORE
    return SOON_BASE - min(days, SOON_HORIZON)


def _load_keywords():
    """Collect lowercase keywords from the user's goals and persona answers."""
    keywords = set()

    info = load_data(get_tasks_file_path("user_info.json"))
    for kw in info.get("goal", []) or []:
        if isinstance(kw, str) and kw.strip():
            keywords.add(kw.lower().strip())

    persona = load_data(get_tasks_file_path("persona.json"))
    for resp in persona.get("responses", []) or []:
        answer = resp.get("answer", "") if isinstance(resp, dict) else ""
        if isinstance(answer, str):
            for word in answer.lower().split():
                word = word.strip(".,;:!?()[]\"'")
                if len(word) > 3:
                    keywords.add(word)

    return keywords


def _keyword_score(title, keywords):
    text = title.lower()
    return KEYWORD_BOOST if any(kw in text for kw in keywords) else 0.0


def prioritize_tasks(tasks=None):
    """Return all tasks as a flat list ordered by priority (highest first).

    Each returned dict carries its ``category``, ``title``, ``deadline``,
    ``created_at``, the computed ``score`` and a 1-based ``rank``. Ranking is
    deadline urgency (overdue > soonest > later > none) plus a small boost when
    the title matches a goal/persona keyword.
    """
    if tasks is None:
        tasks = load_tasks()

    keywords = _load_keywords()
    now = datetime.now()

    scored = []
    for category, task_list in tasks.items():
        for task in task_list:
            title = task.get("title", "")
            deadline = task.get("deadline")
            score = _deadline_score(deadline, now) + _keyword_score(title, keywords)
            scored.append(
                {
                    "category": category,
                    "title": title,
                    "deadline": deadline,
                    "created_at": task.get("created_at", ""),
                    "score": score,
                }
            )

    # Highest score first; older tasks then alphabetical for stable ties.
    scored.sort(key=lambda t: (-t["score"], t["created_at"], t["title"]))

    for rank, task in enumerate(scored, start=1):
        task["rank"] = rank

    return scored


def record_reorder_feedback(moved_title, old_rank, new_rank, new_order):
    """Capture a manual re-rank as feedback and return it.

    Per ``priori.jpeg``: for now this only returns the recorded values —
    callers use them directly.
    """
    # TODO: persist later; see priori.jpeg "we will use this feedback".
    return {
        "moved_title": moved_title,
        "old_rank": old_rank,
        "new_rank": new_rank,
        "new_order": list(new_order),
    }
