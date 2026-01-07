import requests
from bs4 import BeautifulSoup
import datetime
import urllib.parse
import time
import random

# ================= 配置区域 =================
# 核心搜索词
SUBJECT = "高中化学"

# 构造微信公众号专属搜索指令
# 格式：关键词 + site:mp.weixin.qq.com
SEARCH_TASKS = {
    "📢 优质课/公开课 (公众号)": [
        f"{SUBJECT} 优质课大赛 一等奖 site:mp.weixin.qq.com",
        f"{SUBJECT} 课堂实录 教学设计 site:mp.weixin.qq.com",
        f"{SUBJECT} 说课稿 site:mp.weixin.qq.com"
    ],
    "📝 教学论文/干货 (公众号)": [
        f"{SUBJECT} 核心素养 论文 site:mp.weixin.qq.com",
        f"{SUBJECT} 大单元教学 案例 site:mp.weixin.qq.com",
        f"{SUBJECT} 高考备考策略 site:mp.weixin.qq.com"
    ],
    "💡 班主任/名师工作室 (公众号)": [
        f"{SUBJECT} 名师工作室 教学反思 site:mp.weixin.qq.com",
        f"高中班主任 德育案例 site:mp.weixin.qq.com",
        f"化学老师 教学感悟 site:mp.weixin.qq.com"
    ]
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}
# ===========================================

def fetch_wechat_via_bing(query):
    """通过 Bing 搜索定向抓取微信公众号文章"""
    try:
        # Bing 搜索 URL
        url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        
        results = []
        # Bing 结果列表
        items = soup.select('li.b_algo')
        
        for item in items[:5]: # 每个词抓前5条
            h2 = item.find('h2')
            if not h2: continue
            
            link_tag = h2.find('a')
            if not link_tag: continue
            
            title = link_tag.get_text().strip()
            href = link_tag['href']
            
            # 过滤掉非微信域名的杂质 (虽然用了 site 指令，由于广告原因偶尔会有漏网之鱼)
            # 注意：Bing 可能会对链接进行跳转处理，这里我们尽量抓取
            
            # 提取摘要
            snippet_tag = item.select_one('.b_caption p')
            snippet = snippet_tag.get_text().strip()[:80] + "..." if snippet_tag else "点击阅读全文"
            
            # 提取发布时间 (尝试从摘要中提取日期，例如 "2天前", "2023-10-1")
            # Bing 的日期通常在一个 span class="news_dt" 或者摘要开头
            date_tag = item.select_one('span.news_dt')
            date = date_tag.get_text().strip() if date_tag else "近期"

            results.append({
                "title": title,
                "link": href,
                "snippet": snippet,
                "date": date
            })
        return results
    except Exception as e:
        print(f"搜索 '{query}' 失败: {e}")
        return []

def generate_markdown(data_dict):
    md = f"# 🟢 微信公众号精选日报\n\n"
    md += f"**生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC)\n"
    md += "> 本日报定向抓取微信公众号（mp.weixin.qq.com）发布的优质教学资源。\n\n"

    for category, items in data_dict.items():
        md += f"## {category}\n\n"
        if not items:
            md += "今日未抓取到相关内容。\n\n"
            continue
            
        md += "| 文章标题 | 摘要预览 | 发布/收录时间 |\n"
        md += "|---|---|---|\n"
        
        seen_links = set()
        
        for item in items:
            # 简单去重
            if item['link'] in seen_links: continue
            seen_links.add(item['link'])
            
            # 格式化标题
            clean_title = item['title'].replace('|', '-').replace(' - 微信公众平台', '').replace('mp.weixin.qq.com', '')
            clean_snippet = item['snippet'].replace('|', '/')
            
            md += f"| [📄 {clean_title}]({item['link']}) | {clean_snippet} | {item['date']} |\n"
        md += "\n"
        
    return md

def main():
    all_resources = {}
    
    print("🚀 开始抓取微信公众号内容...")
    
    for category, queries in SEARCH_TASKS.items():
        print(f"\n📂 正在处理: {category}")
        category_results = []
        
        for query in queries:
            print(f"  🔍 搜索指令: {query}")
            res = fetch_wechat_via_bing(query)
            category_results.extend(res)
            # 随机延时 2-5 秒，避免 Bing 认为我们是机器人
            time.sleep(random.uniform(2, 5))
            
        all_resources[category] = category_results

    content = generate_markdown(all_resources)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("\n✅ 抓取完成！请查看 README.md")

if __name__ == "__main__":
    main()
