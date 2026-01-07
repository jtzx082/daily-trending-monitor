import requests
from bs4 import BeautifulSoup
import datetime
import urllib.parse
import time
import random

# ================= 配置区域 =================
KEYWORDS = [
    "高中化学",
    "班主任",
    "Gemini"
]

# 模拟真实的浏览器身份，防止被百度拦截
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}
# ===========================================

def fetch_google_rss(keyword):
    """抓取 Google News RSS"""
    try:
        # hl=zh-CN: 界面语言中文, gl=CN: 地理位置中国, ceid=CN:zh-Hans: 区域设置
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        results = []
        for item in items[:5]: # 取前5条
            results.append({
                "title": item.title.text,
                "link": item.link.text,
                "date": item.pubDate.text[:16] if item.pubDate else "",
                "source": "Google"
            })
        return results
    except Exception as e:
        print(f"[Google] 抓取失败: {e}")
        return []

def fetch_bing_rss(keyword):
    """抓取 Bing News RSS"""
    try:
        url = f"https://www.bing.com/news/search?q={urllib.parse.quote(keyword)}&format=rss"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        results = []
        for item in items[:5]:
            results.append({
                "title": item.title.text,
                "link": item.link.text,
                "date": item.pubDate.text[:16] if item.pubDate else "",
                "source": "Bing"
            })
        return results
    except Exception as e:
        print(f"[Bing] 抓取失败: {e}")
        return []

def fetch_baidu_html(keyword):
    """抓取 百度资讯 HTML (难度最高)"""
    try:
        # tn=news: 搜索资讯, rtt=1: 按时间排序(1)或相关性(4)
        url = f"https://www.baidu.com/s?tn=news&rtt=1&bsst=1&cl=2&wd={urllib.parse.quote(keyword)}"
        
        # 百度对 Cookie 有一定校验，这里只做基础请求，如果失败则返回空
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        # 尝试解决中文乱码问题
        response.encoding = 'utf-8' 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 百度资讯的列表通常在 div.result-op 或 div.result 中
        # 标题通常是 h3.news-title_1YtI1 (类名可能会变，用 regex 模糊匹配或找 h3)
        news_items = soup.select('div.result-op, div.result')
        
        results = []
        for item in news_items[:5]:
            # 查找 h3 标签作为标题
            h3_tag = item.find('h3')
            if not h3_tag: continue
            
            link_tag = h3_tag.find('a')
            if not link_tag: continue
            
            title = link_tag.get_text().strip()
            link = link_tag['href']
            
            # 查找发布时间 (通常在 span.c-color-gray2 中)
            date_tag = item.select_one('.c-color-gray2')
            date = date_tag.get_text().strip() if date_tag else "近期"
            
            results.append({
                "title": title,
                "link": link,
                "date": date,
                "source": "Baidu"
            })
        return results
    except Exception as e:
        print(f"[Baidu] 抓取失败: {e}")
        return []

def generate_markdown(data_dict):
    md = f"# 🌍 全网教育与AI资讯日报\n\n"
    md += f"**更新时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC)\n\n"
    
    for keyword, items in data_dict.items():
        md += f"## 📌 {keyword}\n\n"
        if not items:
            md += "今日暂无相关新闻。\n\n"
            continue
            
        md += "| 来源 | 标题 | 时间 |\n"
        md += "|---|---|---|\n"
        
        # 简单去重 (防止不同引擎搜到同一篇文章)
        seen_titles = set()
        
        for news in items:
            # 提取标题前10个字作为去重指纹
            title_fingerprint = news['title'][:10]
            if title_fingerprint in seen_titles:
                continue
            seen_titles.add(title_fingerprint)
            
            # 格式化来源图标
            icon = ""
            if news['source'] == "Google": icon = "🔵 G"
            elif news['source'] == "Bing": icon = "🟢 B"
            elif news['source'] == "Baidu": icon = "🔴 D"
            
            # 清洗标题中的管道符，防止表格错乱
            clean_title = news['title'].replace('|', '-').replace('\n', '')
            
            md += f"| {icon} | [{clean_title}]({news['link']}) | {news['date']} |\n"
        md += "\n"
        
    return md

def main():
    all_news = {}
    
    for keyword in KEYWORDS:
        print(f"\n正在搜索关键词: {keyword} ...")
        
        # 1. 抓取 Google
        g_res = fetch_google_rss(keyword)
        time.sleep(1) # 礼貌性延时
        
        # 2. 抓取 Bing
        b_res = fetch_bing_rss(keyword)
        time.sleep(1)
        
        # 3. 抓取 Baidu
        d_res = fetch_baidu_html(keyword)
        
        # 合并结果
        combined = g_res + b_res + d_res
        all_news[keyword] = combined
        
        print(f"  - Google: {len(g_res)}条, Bing: {len(b_res)}条, Baidu: {len(d_res)}条")
        # 再次延时，防止连续请求不同关键词导致 IP 被封
        time.sleep(random.uniform(2, 5)) 

    # 生成 Markdown
    content = generate_markdown(all_news)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("\nREADME.md 更新成功！")

if __name__ == "__main__":
    main()
