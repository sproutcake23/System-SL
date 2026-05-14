import os
import time
from pathlib import Path
from dotenv import load_dotenv

# LangChain / Google Imports
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

# Custom Scraper
import reddit_scrape as rs

load_dotenv()

# --- CONFIGURATION & PATHS ---
# Using Pathlib for more robust cross-platform path handling
CURRENT_DIR = Path(__file__).parent
VAULT_ROOT = (CURRENT_DIR / "../knowledge_base").resolve()
WIKI_DIR = VAULT_ROOT / "wiki"
RAW_DIR = VAULT_ROOT / "raw"

# Ensure directories exist
WIKI_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

# --- TOOLS ---

@tool
def write_wiki_page(file_name: str, content: str):
    """
    Writes or updates a markdown file in the wiki directory (Pass only the filename to the tool, e.g. 'topic.md'). 
    Use this to maintain the index, log, and entity pages.
    Use page-template in /wiki/templates/page-template for creation of pages in wiki
    file_name: string, the name of the file including .md (e.g., 'index.md').
    content: string, the full markdown text to write.
    """
    path = WIKI_DIR / file_name
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Successfully updated {file_name} in /wiki/"

@tool
def reddit_ingest(top_n: int = 5):
    """
    Scrapes latest deep learning news from Reddit and saves it to the raw folder.
    Returns the content so the agent can process it immediately.
    """
    # Fixed internal variables to prevent API schema errors
    target_domains = ["deeplearning"]
    save_path = RAW_DIR / "reddit_content.md"
    
    # Initialize file with header
    header = f"# Reddit Deep Learning Digest\nGenerated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(header)
    
    # Scrape
    for domain in target_domains:
        # Assuming rs.scrape_feeds handles appending to the file correctly
        rs.scrape_feeds(domain, top_n, str(save_path))

    # Read back for the agent
    if save_path.exists():
        with open(save_path, "r", encoding="utf-8") as f:
            content = f.read()
        return f"Successfully ingested to {save_path.name}. Content:\n\n{content}"
    return "Error: Could not find the generated reddit_content.md file."

# --- AGENT SETUP ---

# Use Gemini 1.5 Flash or Pro for best tool-calling reliability
llm = ChatGoogleGenerativeAI(
    model="models/gemma-4-31b-it", # Highly recommended over Gemma for tool-calling stability
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

# Load System Instructions
instruction_path = VAULT_ROOT / "Instruction.md"
if not instruction_path.exists():
    raise FileNotFoundError(f"Missing Instruction.md at {instruction_path}")

with open(instruction_path, "r", encoding="utf-8") as f:
    system_instructions = f.read()

# Initialize Agent
agent = create_agent(
    model=llm,
    tools=[reddit_ingest, write_wiki_page],
    system_prompt=system_instructions,
)

# --- EXECUTION ---

prompt = """
1. Use the reddit_ingest tool to fetch the top 5 news items.
2. Follow the 'Ingest' workflow:
   - Use page-template in /wiki/templates/page-template for creation of pages in wiki
   - Create or update relevant entity/topic pages in /wiki/ based on the news.
   - Update /wiki/index.md and /wiki/log.md.
3. Summarize exactly which files you created or modified.
"""

result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})

# Flexible printing for different LangChain message formats
last_message = result["messages"][-1]
if hasattr(last_message, 'content'):
    print(last_message.content)
else:
    print(last_message)