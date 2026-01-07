import requests
from bs4 import BeautifulSoup
import datetime
import urllib.parse
import time
import random
import re

# ================= 配置区域 =================
# 基础学科词
SUBJECT = "高中化学"

# 定义三个维度的搜索任务
SEARCH_TASKS = {
    "📄 教学论文/教案 (文档)": [
        f"{SUBJECT} 核心素养 教学论文 filetype:pdf",
        f"{SUBJECT} 大单元教学设计 filetype:doc",
        f"{SUBJECT} 实验改进 论文 filetype:pdf"
    ],
    "💡 教学心得/反思 (知乎/经验)": [
        f"site:zhihu.com {SUBJECT} 教学反思",
        f"site:zhihu.com {SUBJECT} 班主任管理经验",
        f"{SUBJECT} 教学中的困惑与对策"
    ],
    "🏫 经典教学案例": [
        f"{SUBJECT} 优质课 教学设计",
        f"{SUBJECT} 课程思政 教学案例",
        f"{SUBJECT} 探究式教学 案例分析"
    ]
}

# 模拟浏览器头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}
# ===========================================

def fetch_bing_search(query):
    """利用 Bing 搜索获取结果 (最适合搜文件和知乎)"""
    try:
        url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        
        results = []
        # Bing 的搜索结果通常在 li.b_algo 中
        items = soup.select('li.b_algo')
        
        for item in items[:4]: # 每个关键词取前4条
            h2 = item.find('h2')
            if not h2: continue
            
            link_tag = h2.find('a')
            if not link_tag: continue
            
            title = link_tag.get_text().strip()
            href = link_tag['href']
            
            # 提取摘要
            snippet_tag = item.select_one('.b_caption p')
            snippet = snippet_tag.get_text().strip()[:60] + "..." if snippet_tag else "暂无摘要"
            
            results.append({
                "title": title,
                "link": href,
                "snippet": snippet,
                "engine": "Bing"
            })
        return results
    except Exception as e:
        print(f"[Bing] 搜索 '{query}' 失败: {e}")
        return []

def fetch_baidu_search(query):
    """利用 百度 搜索获取结果 (适合搜国内一般文章)"""
    try:
        url = f"https://www.baidu.com/s?wd={urllib.parse.quote(query)}"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        # 百度普通搜索结果容器
        items = soup.select('div.result.c-container')
        
        for item in items[:4]:
            h3 = item.find('h3')
            if not h3: continue
            link_tag = h3.find('a')
            if not link_tag: continue
            
            title = link_tag.get_text().strip()
            href = link_tag['href']
            
            # 百度摘要
            # 百度结构复杂，尝试多种选择器
            snippet = "点击查看详情"
            abstract_tag = item.select_one('.c-abstract') or item.select_one('.content-right_8Zs40')
            if abstract_tag:
                snippet = abstract_tag.get_text().strip()[:60] + "..."

            results.append({
                "title": title,
                "link": href,
                "snippet": snippet,
                "engine": "Baidu"
            })
        return results
    except Exception as e:
        print(f"[Baidu] 搜索 '{query}' 失败: {e}")
        return []

def generate_markdown(data_dict):
    md = f"# 🧪 高中化学教育资源日报\n\n"
    md += f"**生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC)\n"
    md += "> 本日报聚合了教学论文、知乎心得及优质教案资源。\n\n"

    for category, items in data_dict.items():
        md += f"## {category}\n\n"
        if not items:
            md += "今日未抓取到相关内容。\n\n"
            continue
            
        md += "| 标题 | 摘要/关键词 | 来源 |\n"
        md += "|---|---|---|\n"
        
        seen_links = set()
        
        for item in items:
            if item['link'] in seen_links: continue
            seen_links.add(item['link'])
            
            # 标记文件类型
            title_prefix = ""
            if "filetype:pdf" in str(SEARCH_TASKS).lower() and item['link'].endswith('.pdf'):
                title_prefix = "📄 [PDF] "
            elif "filetype:doc" in str(SEARCH_TASKS).lower() and item['link'].endswith('.doc'):
                title_prefix = "📝 [DOC] "
                
            clean_title = item['title'].replace('|', '-').replace('\n', '')
            clean_snippet = item['snippet'].replace('|', '/').replace('\n', '')
            
            md += f"| [{title_prefix}{clean_title}]({item['link']}) | {clean_snippet} | {item['engine']} |\n"
        md += "\n"
        
    return md

def main():
    all_resources = {}
    
    for category, queries in SEARCH_TASKS.items():
        print(f"\n正在处理分类: {category} ...")
        category_results = []
        
        for query in queries:
            print(f"  - 搜索指令: {query}")
            
            # 策略：文档类和知乎类优先用 Bing，其他用 Baidu
            # 这样做是因为 Bing 对 filetype 和 site 指令支持更好
            if "filetype" in query or "site:zhihu" in query:
                res = fetch_bing_search(query)
            else:
                # 随机选择引擎以增加丰富度，或者同时抓取
                res = fetch_baidu_search(query)
                if not res: # 如果百度没抓到（可能被反爬），尝试用 Bing 补救
                     res = fetch_bing_search(query)
            
            category_results.extend(res)
            time.sleep(random.uniform(2, 4)) # 随机延时防封
            
        all_resources[category] = category_results

    # 生成并保存
    content = generate_markdown(all_resources)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("\n资源抓取完成，README.md 已更新！")

if __name__ == "__main__":
    main()
