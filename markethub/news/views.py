# django imports

from django.shortcuts import render
import feedparser
from news.models import NewsArticle
from django.core.paginator import Paginator
from django.core.cache import cache
from bs4 import BeautifulSoup
import yfinance as yf
from django.http import JsonResponse

# Without Model -> NewsArticle

# clean html @ for removing img tag as seen on moneycontrol
def clean_html(raw_html):
    
    # Parse the raw HTML with BeautifulSoup
    soup = BeautifulSoup(raw_html, 'html.parser')

    # Remove all <img> tags (if present)
    for img in soup.find_all('img'):
        img.decompose()  # Remove the img tag completely

    # Return the cleaned text (without any HTML tags)
    return soup.get_text()

# function @ getting live nifty and sensex prices
def get_live_prices():

    nifty = yf.Ticker('^NSEI')
    sensex = yf.Ticker('^BSESN')
    nifty_bank = yf.Ticker('^NSEBANK')
    nifty_it = yf.Ticker('^CNXIT')
    snp500 = yf.Ticker('^GSPC')
    nasdaq = yf.Ticker('^IXIC')
    # dow30 = yf.Ticker('^DJI')

    nifty_price = nifty.history(period="1d")['Close'].iloc[-1]
    sensex_price = sensex.history(period="1d")['Close'].iloc[-1]
    nifty_bank_price = nifty_bank.history(period="1d")['Close'].iloc[-1]
    nifty_it_price = nifty_it.history(period="1d")['Close'].iloc[-1]
    snp500_price = snp500.history(period="1d")['Close'].iloc[-1]
    nasdaq_price = nasdaq.history(period="1d")['Close'].iloc[-1]
    # dow30_price = dow30.history(period="1d")['Close'].iloc[-1]

    return {
        'nifty_price': nifty_price,
        'sensex_price': sensex_price,
        'nifty_bank_price' : nifty_bank_price,
        'nifty_it_price' : nifty_it_price,
        'snp500_price' : snp500_price,
        'nasdaq_price' : nasdaq_price,
        # 'dow30_price' : dow30_price
    }

# function @ refreshing prices every 2 seconds
def get_prices(request):
    prices = get_live_prices()
    return JsonResponse(prices)



def home(request):

    # rss feeds
    
    rss_urls = [

    	# Indian Markets
    	'https://economictimes.indiatimes.com/rssfeedsdefault.cms',
        'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms',
        'https://economictimes.indiatimes.com/prime/money-and-markets/rssfeeds/62511286.cms',
        'https://www.moneycontrol.com/rss/latestnews.xml',
        'https://www.business-standard.com/rss/home_page_top_stories.rss',
        'https://www.livemint.com/rss/markets',
        'https://www.livemint.com/rss/money',
        'https://www.thehindubusinessline.com/news/feeder/default.rss',
        'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms',
        'https://www.business-standard.com/rss/markets-106.rss',
        'https://feeds.feedburner.com/ndtvprofit-latest',
        'https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms',
        'https://www.ndtvprofit.com/stories.rss',
        'https://www.thehindu.com/business/Economy/feeder/default.rss',
        'https://www.thehindu.com/business/markets/feeder/default.rss',
        'https://economictimes.indiatimes.com/wealth/mutual-funds/rssfeeds/49995327.cms',
        'https://economictimes.indiatimes.com/tech/funding/rssfeeds/78570550.cms',
        'https://economictimes.indiatimes.com/wealth/personal-finance-news/rssfeeds/49674901.cms',
        'https://economictimes.indiatimes.com/wealth/rssfeeds/837555174.cms',
        

        # Asian Markets
        'https://www.reuters.com/markets/asia/?format=xml',
        'https://www.scmp.com/rss/2/feed',

        # US Markets
        'https://www.reuters.com/markets/us?format=xml',
        'https://www.cnbc.com/id/10001147/device/rss/rss.html',
        'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
        'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^DJI&region=US&lang=en-US',

        # not working 
        'https://www.business-standard.com/rss/markets-106.rss',
        'https://www.business-standard.com/rss/economy-102.rss',
        'https://www.business-standard.com/rss/finance-103.rss',
        'https://www.business-standard.com/rss/finance/personal-finance-10313.rss',
        'https://www.business-standard.com/rss/finance/investment-10315.rss',
        'https://www.business-standard.com/rss/markets-106.rss',
        'https://www.business-standard.com/rss/markets/commodities-10608.rss',
        'https://www.business-standard.com/rss/markets/stock-market-news-10618.rss',

     ] 


    # News Logic
    all_entries = []
    seen_titles = set()  # Set to track unique titles or links

    for rss_url in rss_urls:
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                # Use title or link to filter duplicates
                if entry.title not in seen_titles:
                    # Clean the title and description using BeautifulSoup
                    entry.title = clean_html(entry.title)
                    entry.description = clean_html(entry.description)
                    
                    all_entries.append(entry)
                    seen_titles.add(entry.title)  # Mark this title as seen
        except Exception as e:
            print(f"Error fetching {rss_url}: {e}")

    all_entries.sort(key=lambda entry: entry.published_parsed, reverse=True)

    # Cache the combined and filtered entries for 1 hour (3600 seconds)
    cache.set('rss_news', all_entries, timeout=3600)

    # Pagination Logic
    # Show 50 news items per page and next in next and prev
    paginator = Paginator(all_entries, 50)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    # Logic for price 
    # Get live prices
    prices = get_live_prices()


    context = {
        # context for news with pagination
        'feed': page_obj,
        # context for market prices
        'nifty_price': prices['nifty_price'],
        'sensex_price': prices['sensex_price'],
        'nifty_bank_price': prices['nifty_bank_price'],
        'nifty_it_price' : prices['nifty_it_price'],
        'snp500_price' : prices['snp500_price'],
        'nasdaq_price' : prices['nasdaq_price'],
        # 'dow30_price' : prices['dow30_price'],


    }
    

    return render(request , 'home.html' , context)





