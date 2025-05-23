import random
from datetime import datetime

def get_latest_news(api_key: str = "DUMMY_NEWS_API_KEY"):
    '''
    Simulates fetching the latest financial news summary.
    In a real implementation, this would call a news API (e.g., NewsAPI.org, Alpha Vantage News).
    
    Args:
        api_key (str): The API key for the news service. Not used in dummy version.
                       It's good practice to include it in the function signature if needed by the real one.
                       
    Returns:
        str: A simulated news summary string.
    '''
    print(f"Simulating fetching latest news (using dummy API key: {api_key})...")
    
    # Dummy news summaries
    summaries = [
        "Tech stocks rally on positive earnings reports from major companies.",
        "Federal Reserve signals potential interest rate hikes to combat rising inflation.",
        "Oil prices surge due to geopolitical tensions and supply concerns.",
        "New government regulations impact the renewable energy sector.",
        "Market experiences a slight downturn amidst uncertainty in global trade.",
        "Cryptocurrency market sees increased volatility after a major exchange announcement.",
        "Startup X secures significant funding, boosting investor confidence in the sector.",
        "Consumer spending data shows unexpected growth, leading to optimistic market sentiment.",
        "Inflation figures remain stable, easing fears of aggressive monetary policy.",
        "Major corporation announces stock buyback program, share prices increase."
    ]
    
    selected_summary = random.choice(summaries)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    full_report = f"[{timestamp}] {selected_summary}"
    
    print(f"  -> Simulated news: {full_report}")
    return full_report

if __name__ == '__main__':
    print("Running fetch_news.py directly for testing...")
    
    news_item1 = get_latest_news()
    print(f"Fetched news item 1: {news_item1}")
    
    news_item2 = get_latest_news(api_key="ANOTHER_DUMMY_KEY")
    print(f"Fetched news item 2: {news_item2}")
