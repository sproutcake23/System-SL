# import urllib.request
# import json
# import time

# def fetch_hn_by_domain(domain, top_n=5):
#     # This query searches for the domain specifically
#     url = f"https://hn.algolia.com/api/v1/search?query={domain}&restrictSearchableAttributes=url"
    
#     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ScraperBot/1.0'}
    
#     try:
#         req = urllib.request.Request(url, headers=headers)
#         with urllib.request.urlopen(req) as response:
#             data = json.loads(response.read().decode('utf-8'))
            
#         hits = data.get('hits', [])
        
#         with open("hn_domain_results.md", "a", encoding="utf-8") as file:
#             file.write(f"\n# 🔍 Hacker News results for: {domain}\n\n")
            
#             for hit in hits[:top_n]:
#                 title = hit.get('title')
#                 link = hit.get('url')
#                 author = hit.get('author')
#                 hn_id = hit.get('objectID')
#                 hn_link = f"https://news.ycombinator.com/item?id={hn_id}"
                
#                 # Check for story_text (HN's version of self_text)
#                 story_text = hit.get('story_text', '')

#                 file.write(f"### {title}\n")
#                 file.write(f"**Author:** u/{author} | **Link:** [Direct]({link})\n\n")
                
#                 if story_text:
#                     # Basic cleaning if there is text
#                     file.write(f"> {story_text[:200]}...\n\n")
                
#                 file.write(f"💬 [View HN Discussion]({hn_link})\n\n")
#                 file.write("---\n")
                
#         print(f"Successfully fetched {domain} from HN.")

#     except Exception as e:
#         print(f"Error fetching domain {domain}: {e}")

# # Example Usage
# if __name__ == "__main__":
#     # Clear the file first
#     with open("hn_domain_results.md", "w", encoding="utf-8") as f:
#         f.write("# HN Domain Search Results\n\n")
        
#     domains_to_search = ["github.com", "openai.com", "arxiv.org"]
#     for d in domains_to_search:
#         fetch_hn_by_domain(d)
#         time.sleep(1) # Be polite to Algolia


import urllib.request
import json
import time

# Define your categories and the keywords to trigger them
CATEGORIES = {
    "Artificial Intelligence": "AI, LLM, OpenAI, Transformer, GPT",
    "Deep Learning": "Neural Network, PyTorch, TensorFlow, Keras",
    "Web Development": "React, TypeScript, Rust, Bun, CSS, Backend",
    "Cybersecurity": "CVE, Exploit, Vulnerability, Encryption"
}

def fetch_hn_by_topic(topic_name, keywords):
    # We use search_by_date to get the most recent relevant news
    # Encoding the keywords for a URL
    query = keywords.replace(", ", "%20OR%20")
    url = f"https://hn.algolia.com/api/v1/search_by_date?query={query}&tags=story"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        hits = data.get('hits', [])
        
        with open("hn_classified.md", "a", encoding="utf-8") as file:
            file.write(f"## 📂 Category: {topic_name}\n\n")
            
            for hit in hits[:5]: # Top 5 for each category
                title = hit.get('title')
                hn_link = f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                external_link = hit.get('url') or hn_link
                author = hit.get('author')

                file.write(f"### {title}\n")
                file.write(f"**Author:** u/{author}\n")
                file.write(f"🔗 [Link]({external_link}) | 💬 [Discussion]({hn_link})\n\n")
            
            file.write("---\n")
            
    except Exception as e:
        print(f"Error fetching {topic_name}: {e}")

if __name__ == "__main__":
    with open("hn_classified.md", "w", encoding="utf-8") as f:
        f.write("# Hacker News Classified Digest\n\n")

    for category, keywords in CATEGORIES.items():
        print(f"Fetching {category}...")
        fetch_hn_by_topic(category, keywords)
        time.sleep(1) # API politeness