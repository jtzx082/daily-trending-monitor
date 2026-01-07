import requests
import os
from typing import List, Dict

class GoogleSearch:
    """Google Custom Search API"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.cx = os.getenv('GOOGLE_CX')
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """使用Google Custom Search API"""
        if not self.api_key or not self.cx:
            print("警告: Google API密钥未设置，跳过Google搜索")
            return []
        
        results = []
        try:
            # Google API限制每页最多10个结果
            pages = (num_results + 9) // 10
            
            for page in range(pages):
                start = page * 10 + 1
                params = {
                    'key': self.api_key,
                    'cx': self.cx,
                    'q': query,
                    'num': min(10, num_results - page * 10),
                    'start': start,
                    'lr': 'lang_en'
                }
                
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if 'items' in data:
                    for item in data['items']:
                        results.append({
                            'title': item.get('title', ''),
                            'link': item.get('link', ''),
                            'snippet': item.get('snippet', '')
                        })
                
                if len(results) >= num_results:
                    break
        
        except Exception as e:
            print(f"Google搜索错误: {e}")
        
        return results[:num_results]
