import feedparser
import ssl
import urllib.request
import time
import json

domains = ["deeplearning"]

def reddit_link_template(domain, format_type):
    return f"https://www.reddit.com/r/{domain}/.{format_type}"

def scrape_feeds(domain, top_n):
    all_articles = []
    
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    url = reddit_link_template(domain, "rss") 
    print(f"--- Scraping {url} ---")
        
    try:
        # User-Agent is vital to avoid 429 errors
        req_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ScraperBot/1.1'}
        
        rss_req = urllib.request.Request(url, headers=req_headers)
        with urllib.request.urlopen(rss_req) as response:
            content = response.read()
        
        feed = feedparser.parse(content)

        for entry in feed.entries[:top_n]:
            # Clean the link for JSON request
            base_link = entry.link.rstrip('/')
            json_url = f"{base_link}.json"
            
            try:    
                json_req = urllib.request.Request(json_url, headers=req_headers)
                with urllib.request.urlopen(json_req) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode('utf-8'))
                        
                        # --- POST DATA EXTRACTION ---
                        post_info = data[0]['data']['children'][0]['data']
                        post_author = post_info.get('author', 'Unknown')
                        self_text = post_info.get('selftext', '')
                        external_url = post_info.get('url', '') # The link if it's a link post
                        
                        # --- COMMENTS EXTRACTION ---
                        comments_list = data[1]['data']['children']
                        top_3_comments = comments_list[:3]

                        # --- WRITE TO MARKDOWN ---
                        with open("reddit_content.md", "a", encoding="utf-8") as file:
                            file.write(f"# {entry.title}\n\n")
                            file.write(f"**Post Author:** u/{post_author}  \n")
                            file.write(f"**Reddit Link:** [View Discussion]({base_link})\n\n")
                            
                            # If self_text exists, show it. 
                            # If not, and the external_url is different from the reddit link, it's a link post.
                            if self_text:
                                file.write("## Post Content\n")
                                file.write(f"{self_text}\n\n")
                            elif external_url and "reddit.com" not in external_url:
                                file.write("## External Link\n")
                                file.write(f"🔗 [Direct Link to Content]({external_url})\n\n")

                            file.write("## Top Discussions\n\n")
                            for i, comment in enumerate(top_3_comments, 1):
                                if comment['kind'] == 't1':
                                    c_data = comment['data']
                                    file.write(f"### Chat #{i} by u/{c_data['author']}\n")
                                    file.write(f"> {c_data['body']}\n\n")
                            
                            file.write("---\n\n") 

                        print(f"Successfully saved: {entry.title}")
                
                # Sleep to respect Reddit API limits
                time.sleep(0.5) 

            except Exception as e:
                print(f"Error fetching {json_url}: {e}")
                
    except Exception as e:
        print(f"Error scraping {domain}: {e}")

if __name__ == "__main__":
    # Create file and write a clean header
    with open("reddit_content.md", "w", encoding="utf-8") as f:
        f.write("# Reddit Deep Learning Digest\n")
        f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # for domain in domains:
    #     scrape_feeds(domain, 10)


    # import feedparser

    # Replace 'hn_feed.xml' with the path to your file, or pass the raw string
    # If you have the data in a string variable, use: feed = feedparser.parse(xml_string)


    feed = feedparser.parse("https://hnrss.org/frontpage")
    with open("hacker_news.md", "w", encoding="utf-8") as f:
        f.write("# Hacker News\n")
        f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for entry in feed.entries[:10]:
            f.write(f"- [{entry.title}]({entry.link})\n\n")

