import requests
import json

class PageSpeedAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    def get_pagespeed_data(self, url, strategy="mobile"):
        params = {
            'url': url,
            'key': self.api_key,
            'strategy': strategy,
            'category': ['performance', 'accessibility', 'best-practices', 'seo']
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        return {
            'url': url,
            'strategy': strategy,
            'performance_score': data['lighthouseResult']['categories']['performance']['score'] * 100,
            'lcp': data['lighthouseResult']['audits']['largest-contentful-paint']['displayValue'],
            'fid': data['lighthouseResult']['audits']['max-potential-fid']['displayValue'],
            'cls': data['lighthouseResult']['audits']['cumulative-layout-shift']['displayValue'],
            'fcp': data['lighthouseResult']['audits']['first-contentful-paint']['displayValue'],
            'tti': data['lighthouseResult']['audits']['interactive']['displayValue'],
            'speed_index': data['lighthouseResult']['audits']['speed-index']['displayValue'],
            'tbt': data['lighthouseResult']['audits']['total-blocking-time']['displayValue']
        }

# Example usage
if __name__ == "__main__":
    ps = PageSpeedAPI("YOUR_API_KEY")
    data = ps.get_pagespeed_data("https://example.com")
    print(json.dumps(data, indent=2))