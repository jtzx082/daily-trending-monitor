import requests
from bs4 import BeautifulSoup
import datetime
import urllib.parse

# 定义您想要关注的关键词（可以在这里随意增减）
KEYWORDS = [
    "高中化学",
    "班主任工作",
    "Gemini"
]

def fetch_bing_news_rss(keyword):
    # 将关键词转换为 URL 编码 (例如: 高中 -> %E9%AB%98%E4%B8%AD)
    encoded_keyword = urllib.parse.quote(keyword)
    # Bing News RSS 接口
    url = f"https://www.bing.com/news/search?q={encoded_keyword}&format=rss"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 使用 xml 解析器
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        news_list = []
        for item in items[:10]: # 每个话题只取前10条
            title = item.title.text
            link = item.link.text
            pub_date = item.pubDate.text if item.pubDate else ""
            
            # 简单的日期格式化，去掉多余的时区信息
            if len(pub_date) > 16:
                pub_date = pub_date[:16]
                
            news_list.append({
                "title": title,
                "link": link,
                "date": pub_date
            })
            
        return news_list

    except Exception as e:
        print(f"获取 [{keyword}] 失败: {e}")
        return []

def generate_markdown(data_dict):
    md = f"# 🏫 教育与科技日报\n\n"
    md += f"**更新时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC)\n\n"
    md += "> 本日报由 GitHub Actions 自动生成，数据来源 Bing News。\n\n"

    for keyword, news_items in data_dict.items():
        md += f"## 📌 {keyword}\n\n"
        if not news_items:
            md += "今日暂无相关新闻。\n\n"
            continue
            
        md += "| 新闻标题 | 发布时间 |\n"
        md += "|---|---|\n"
        for news in news_items:
            # 清理标题中的 Bing 高亮标签
            clean_title = news['title'].replace(f"{keyword}", f"**{keyword}**")
            md += f"| [{clean_title}]({news['link']}) | {news['date']} |\n"
        md += "\n"
        
    return md

def main():
    all_news = {}
    
    for keyword in KEYWORDS:
        print(f"正在抓取: {keyword} ...")
        news = fetch_bing_news_rss(keyword)
        all_news[keyword] = news
    
    # 生成 Markdown 内容
    content = generate_markdown(all_news)
    
    # 保存文件
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("README.md 更新成功！")

if __name__ == "__main__":
    main()
