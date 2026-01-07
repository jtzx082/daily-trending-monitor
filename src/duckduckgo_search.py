import requests
import time
from typing import List, Dict
import random

class DuckDuckGoSearch:
    """DuckDuckGo 搜索（无需API密钥）"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        使用DuckDuckGo搜索
        返回: [{'title': str, 'link': str, 'snippet': str}]
        """
        try:
            # DuckDuckGo HTML搜索
            url = "https://html.duckduckgo.com/html/"
            params = {
                'q': query,
                'kl': 'us-en',
                'kp': 1,  # 关闭安全搜索
            }
            
            response = self.session.post(url, data=params, timeout=30)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result in soup.find_all('div', class_='result'):
                try:
                    title_elem = result.find('a', class_='result__title')
                    link_elem = result.find('a', class_='result__url')
                    snippet_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem and link_elem:
                        link = link_elem.get('href')
                        if link and not link.startswith('//duckduckgo.com'):
                            results.append({
                                'title': title_elem.text.strip(),
                                'link': link,
                                'snippet': snippet_elem.text.strip() if snippet_elem else ''
                            })
                    
                    if len(results) >= max_results:
                        break
                        
                except Exception as e:
                    continue
            
            # 随机延迟防止被封
            time.sleep(random.uniform(1, 3))
            return results
            
        except Exception as e:
            print(f"DuckDuckGo搜索错误: {e}")
            return []
    
    def search_multiple_queries(self, queries: List[str], results_per_query: int = 10) -> List[Dict]:
        """搜索多个查询词"""
        all_results = []
        for query in queries:
            print(f"搜索: {query}")
            results = self.search(query, results_per_query)
            all_results.extend(results)
            time.sleep(random.uniform(2, 4))  # 查询间延迟
        
        # 去重
        seen_links = set()
        unique_results = []
        for result in all_results:
            if result['link'] not in seen_links:
                seen_links.add(result['link'])
                unique_results.append(result)
        
        return unique_results
