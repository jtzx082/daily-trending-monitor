import requests
from bs4 import BeautifulSoup
import datetime
import os

def scrape_github_trending():
    url = "https://github.com/trending"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        repo_list = soup.select('article.Box-row') # 获取所有项目卡片
        
        markdown_content = f"# 📈 GitHub 开源项目日报\n\n"
        markdown_content += f"**更新时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC)\n\n"
        markdown_content += "| 项目名称 | 简介 | Stars |\n"
        markdown_content += "|---|---|---|\n"

        for repo in repo_list[:15]: # 只取前15个
            # 1. 提取项目名称和链接
            h1 = repo.select_one('h1')
            link = h1.select_one('a')
            name = link.text.strip().replace('\n', '').replace(' ', '')
            href = f"https://github.com{link['href']}"
            
            # 2. 提取描述 (有些项目没有描述，需要容错)
            desc_tag = repo.select_one('p.col-9')
            desc = desc_tag.text.strip() if desc_tag else "暂无描述"
            
            # 3. 提取今日 Star 数 (通常在最后一个 svg 后面)
            # 这里简化处理，直接找包含 'stars today' 的文本
            stars_today = "N/A"
            span_tags = repo.select('span.d-inline-block.float-sm-right')
            if span_tags:
                stars_today = span_tags[0].text.strip()
            
            # 为了防止 Markdown 表格错乱，替换掉描述里的竖线
            desc = desc.replace('|', '/')
            
            markdown_content += f"| [{name}]({href}) | {desc} | {stars_today} |\n"

        return markdown_content

    except Exception as e:
        print(f"爬取失败: {e}")
        return None

def save_to_file(content):
    # 将结果保存为 README.md，这样直接在仓库首页就能看到
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("文件已更新: README.md")

if __name__ == "__main__":
    content = scrape_github_trending()
    if content:
        save_to_file(content)
