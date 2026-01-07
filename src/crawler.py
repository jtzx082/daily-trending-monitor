#!/usr/bin/env python3
"""
Q7DTD 密钥爬虫 - GitHub Actions 版本
"""

import requests
import re
import time
import random
import json
import os
from typing import List, Set, Dict
from datetime import datetime
from urllib.parse import urlparse

# 导入搜索模块
try:
    from duckduckgo_search import DuckDuckGoSearch
    from google_search import GoogleSearch
except ImportError:
    from .duckduckgo_search import DuckDuckGoSearch
    from .google_search import GoogleSearch

class Q7DTDCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        })
        
        # 初始化搜索引擎
        self.ddg = DuckDuckGoSearch()
        self.google = GoogleSearch() if os.getenv('GOOGLE_API_KEY') else None
        
        # 搜索查询列表
        self.search_queries = [
            'Q7DTD',
            '"Q7DTD" key',
            '"Q7DTD" license',
            '"Q7DTD" activation',
            '"Q7DTD" serial',
            'Q7DTD code',
            'Q7DTD password',
            'Q7DTD token',
            'filetype:txt Q7DTD',
            'filetype:json Q7DTD',
            'site:pastebin.com Q7DTD',
            'site:github.com Q7DTD',
            'site:gitlab.com Q7DTD',
            'site:bitbucket.org Q7DTD',
            'Q7DTD API key',
            'Q7DTD secret',
        ]
        
        # 密钥正则模式
        self.key_patterns = [
            r'Q7DTD[a-zA-Z0-9]{8,64}',  # Q7DTD前缀
            r'[A-Z0-9]{10,64}Q7DTD[A-Z0-9]{0,64}',  # 包含Q7DTD
            r'[a-fA-F0-9]{32,128}',  # 哈希格式
            r'[A-Z]{3,20}[0-9]{3,20}[A-Z]{3,20}',  # 字母数字混合
        ]
    
    def extract_keys_from_text(self, text: str) -> Set[str]:
        """从文本中提取可能的密钥"""
        keys = set()
        text_upper = text.upper()
        
        # 如果文本包含Q7DTD
        if 'Q7DTD' in text_upper:
            # 按行分割，处理包含Q7DTD的行
            for line in text.split('\n'):
                line_upper = line.upper()
                if 'Q7DTD' in line_upper:
                    # 尝试各种模式
                    for pattern in self.key_patterns:
                        matches = re.findall(pattern, line, re.IGNORECASE)
                        for match in matches:
                            if 'Q7DTD' in match.upper():
                                # 清理密钥
                                clean_key = match.strip().strip('"\',.;:!?')
                                if 10 <= len(clean_key) <= 128:  # 合理长度
                                    keys.add(clean_key)
        
        return keys
    
    def fetch_url_content(self, url: str, timeout: int = 15) -> str:
        """获取URL内容"""
        try:
            # 添加referer
            headers = self.session.headers.copy()
            headers['Referer'] = 'https://www.google.com/'
            
            response = self.session.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '').lower()
            if 'text' in content_type or 'json' in content_type or 'xml' in content_type:
                return response.text
            else:
                print(f"  跳过非文本内容: {content_type}")
                return ''
                
        except Exception as e:
            print(f"  获取URL失败 {url}: {e}")
            return ''
    
    def crawl_url(self, url: str) -> Set[str]:
        """爬取单个URL"""
        print(f"  爬取: {url[:80]}...")
        
        # 随机延迟
        time.sleep(random.uniform(1, 3))
        
        content = self.fetch_url_content(url)
        if not content:
            return set()
        
        keys = self.extract_keys_from_text(content)
        return keys
    
    def search_and_crawl(self, use_google: bool = True) -> Dict[str, List[str]]:
        """执行搜索和爬取"""
        all_keys = set()
        crawled_urls = set()
        
        print("开始搜索...")
        
        # DuckDuckGo搜索
        print("\n=== DuckDuckGo搜索 ===")
        ddg_results = self.ddg.search_multiple_queries(self.search_queries, results_per_query=5)
        print(f"找到 {len(ddg_results)} 个DuckDuckGo结果")
        
        # Google搜索（如果有API密钥）
        google_results = []
        if use_google and self.google:
            print("\n=== Google搜索 ===")
            for query in self.search_queries[:8]:  # 限制查询数量
                print(f"搜索: {query}")
                results = self.google.search(query, 5)
                google_results.extend(results)
                time.sleep(1)  # API速率限制
            print(f"找到 {len(google_results)} 个Google结果")
        
        # 合并结果
        all_results = ddg_results + google_results
        print(f"\n总共找到 {len(all_results)} 个搜索结果")
        
        # 去重URL
        unique_urls = []
        for result in all_results:
            url = result['link']
            if url not in crawled_urls:
                parsed = urlparse(url)
                # 过滤掉不需要的域名
                if parsed.netloc and not any(x in parsed.netloc for x in ['facebook.com', 'twitter.com', 'youtube.com']):
                    crawled_urls.add(url)
                    unique_urls.append(url)
        
        print(f"去重后剩下 {len(unique_urls)} 个URL")
        
        # 爬取每个URL
        print("\n=== 开始爬取URL ===")
        for i, url in enumerate(unique_urls[:30]):  # 限制爬取数量
            print(f"[{i+1}/{len(unique_urls[:30])}] ", end='')
            keys = self.crawl_url(url)
            if keys:
                print(f"    找到 {len(keys)} 个密钥")
                all_keys.update(keys)
            
            # 随机延迟
            if i < len(unique_urls[:30]) - 1:
                time.sleep(random.uniform(2, 4))
        
        return {
            'keys': list(all_keys),
            'urls_crawled': len(unique_urls[:30]),
            'search_results': len(all_results),
            'timestamp': datetime.now().isoformat()
        }
    
    def save_results(self, results: dict, filename: str = 'results.json'):
        """保存结果到文件"""
        # 确保results目录存在
        os.makedirs('results', exist_ok=True)
        
        filepath = os.path.join('results', filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # 同时保存纯文本版本
        txt_path = os.path.join('results', 'keys.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"# Q7DTD Keys Found\n")
            f.write(f"# Date: {results['timestamp']}\n")
            f.write(f"# URLs Crawled: {results['urls_crawled']}\n")
            f.write(f"# Search Results: {results['search_results']}\n")
            f.write(f"# Total Keys Found: {len(results['keys'])}\n")
            f.write("=" * 50 + "\n\n")
            
            for key in sorted(results['keys']):
                f.write(f"{key}\n")
        
        print(f"\n结果已保存到: {filepath}")
        print(f"文本版本: {txt_path}")
        
        return filepath

def main():
    """主函数"""
    print("=" * 60)
    print("Q7DTD 密钥爬虫 - GitHub Actions 版本")
    print("=" * 60)
    
    # 创建爬虫实例
    crawler = Q7DTDCrawler()
    
    # 判断是否使用Google API
    use_google = bool(os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_CX'))
    
    # 执行爬取
    start_time = time.time()
    results = crawler.search_and_crawl(use_google=use_google)
    elapsed_time = time.time() - start_time
    
    # 添加统计信息
    results['elapsed_time'] = round(elapsed_time, 2)
    results['keys_count'] = len(results['keys'])
    
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'q7dtd_results_{timestamp}.json'
    
    # 保存结果
    crawler.save_results(results, filename)
    
    # 输出摘要
    print("\n" + "=" * 60)
    print("爬取完成!")
    print(f"耗时: {elapsed_time:.2f} 秒")
    print(f"搜索到: {results['search_results']} 个结果")
    print(f"爬取了: {results['urls_crawled']} 个URL")
    print(f"找到密钥: {results['keys_count']} 个")
    
    if results['keys']:
        print("\n找到的密钥（前10个）:")
        for key in list(results['keys'])[:10]:
            print(f"  {key}")
        if len(results['keys']) > 10:
            print(f"  ... 和 {len(results['keys']) - 10} 个更多")
    else:
        print("\n未找到包含Q7DTD的密钥")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
