from playwright.sync_api import sync_playwright
import json
import time

class WebsiteCrawler:
    def __init__(self, url, max_depth=3, max_urls=500):
        self.url = url
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.results = []

    def crawl(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # Handle cookie banner
            self.handle_cookie_banner(page)
            
            # Crawl the site
            self._crawl_page(page, self.url, 0)
            
            browser.close()
        
        return self.results

    def handle_cookie_banner(self, page):
        # Load selectors from config
        with open('../config/cookie_selectors.json') as f:
            selectors = json.load(f)
        
        page.goto(self.url)
        time.sleep(2)  # Wait for banner
        
        for selector in selectors['cookie_banner_selectors']['generic']:
            try:
                page.click(selector, timeout=3000)
                print(f"Clicked cookie banner with {selector}")
                break
            except:
                continue

    def _crawl_page(self, page, url, depth):
        if depth > self.max_depth or len(self.results) >= self.max_urls:
            return
        
        try:
            page.goto(url)
            time.sleep(1)
            
            # Extract data
            data = {
                'url': url,
                'status': page.status,
                'title': page.title(),
                'h1': page.locator('h1').count(),
                'images': page.locator('img').count(),
                'images_without_alt': page.locator('img:not([alt])').count(),
                'page_size': len(page.content())
            }
            
            self.results.append(data)
            
            # Find links
            links = page.locator('a').all()
            for link in links[:10]:  # Limit for demo
                href = link.get_attribute('href')
                if href and href.startswith(self.url):
                    self._crawl_page(page, href, depth + 1)
                    
        except Exception as e:
            print(f"Error crawling {url}: {e}")

if __name__ == "__main__":
    crawler = WebsiteCrawler("https://example.com")
    results = crawler.crawl()
    print(json.dumps(results, indent=2))