import os
import subprocess
import platform   
import time
import reddit_scrape as rs
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from dotenv import load_dotenv

domains = ["deeplearning"]

load_dotenv()
# 1. Define the tool with a decorator
@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@tool
def reddit(top_n: int) :
    """Function scrapes the latest news from reddit and saves in reddit_content.md
    
    args:

    top_n: int => No. of news to be returned from each domain

    """

    domains = ["deeplearning"]

    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 2. Join it with the name of the file you want to run
    save_path = os.path.join(current_dir, "scrape_content/reddit_content.md")
    # Create file and write a clean header
    with open(save_path, "w", encoding="utf-8") as f:
        f.write("# Reddit Deep Learning Digest\n")
        f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    for domain in domains:
        rs.scrape_feeds(domain, top_n)



    def open_file(path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])

    # Call the function after your file writing logic
    open_file(save_path)

    with open(save_path, "r", encoding="utf-8") as f:
        content = f.read()
        content.encode('utf-8', 'ignore').decode('utf-8')
        
    # CRITICAL: Return the content so Gemini can see it!
    return f"Success! Data saved to output.md. Here is the content: \n\n{content}"


# 2. Initialize the model object
# You can also use model="google_genai:gemini-1.5-flash" as a string
llm = ChatGoogleGenerativeAI(
    model="models/gemma-4-31b-it", 
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# 3. Create the agent
agent = create_agent(
    model=llm,
    tools=[get_weather, reddit],
    system_prompt="You are a helpful assistant",
)

# 4. Invoke and print the final content
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the top 5 latest news in reddit?"}]}
)

# In v1, the last message is an AIMessage; use .content to see the text
print(result["messages"][-1].content[-1]['text'])

