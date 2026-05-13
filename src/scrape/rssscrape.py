import feedparser
import ssl
import urllib.request

# A list of 'Popular Links' as RSS feeds
news_sources = {
    # "The Verge": "https://www.theverge.com/rss/index.xml",
    "Reddit Tech": "https://www.reddit.com/r/deeplearning/.rss",
#     "Hacker News": "https://news.ycombinator.com/rss",
 }


def scrape_feeds(sources):
    all_articles = []   
    
    # SSL bypass for local environments
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    for name, url in sources.items():
        print(f"--- Scraping {name} ---")
        
        try:
            # 1. Define the Request with a User-Agent
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            # 2. Open the URL and read the content
            with urllib.request.urlopen(req) as response:
                content = response.read()
                print(content)
            
            # 3. Pass the raw content to feedparser
            feed = feedparser.parse(content)

            if not feed.entries:
                print(f"No entries found for {name}.\n")
                continue

            for entry in feed.entries[:5]:
                article_data = {
                    "source": name,
                    "title": entry.title,
                    "link": entry.link,
                }
                all_articles.append(article_data)
                print(f"Title: {article_data['title']}\n")
                
        except Exception as e:
            print(f"Error scraping {name}: {e}")

    return all_articles

# Your sources dictionary remains the same

# Run the scraper
scraped_data = scrape_feeds(news_sources)
