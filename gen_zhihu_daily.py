import requests
import json
import datetime
import PyRSS2Gen
import re

# 获取知乎日报内容
def get_zhihu_news():
    url = "https://news-at.zhihu.com/api/3/news/latest"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

# 获取单篇文章详情
def get_news_detail(news_id):
    url = f"https://news-at.zhihu.com/api/3/news/{news_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

# 生成 RSS
def generate_rss():
    news_data = get_zhihu_news()
    items = []
    
    # 处理每篇文章
    for story in news_data.get('stories', []):
        try:
            detail = get_news_detail(story['id'])
            title = detail.get('title', '')
            body = detail.get('body', '')
            image = detail.get('image', '')
            share_url = detail.get('share_url', '')
            
            # 构建带图片的 HTML 内容 - 注意：这里不进行任何转义
            html_content = f'<div class="main-img" style="margin-bottom: 20px;"><img src="{image}" style="max-width:100%; border-radius: 8px;"></div>' + body
            
            # 创建 RSS 项
            item = PyRSS2Gen.RSSItem(
                title=title,
                link=share_url,
                description=html_content,  # 原始 HTML 内容
                guid=PyRSS2Gen.Guid(share_url),
                pubDate=datetime.datetime.utcnow()
            )
            items.append(item)
        except Exception as e:
            print(f"Error processing story {story.get('id', 'unknown')}: {e}")
            continue
    
    # 创建 RSS
    rss = PyRSS2Gen.RSS2(
        title="知乎日报",
        link="https://daily.zhihu.com/",
        description="知乎日报 RSS feed",
        lastBuildDate=datetime.datetime.utcnow(),
        items=items
    )
    
    # 生成 XML
    rss_xml = rss.to_xml(encoding='utf-8')
    
    # 确保我们处理的是字符串
    if isinstance(rss_xml, bytes):
        rss_xml = rss_xml.decode('utf-8')
    
    # 关键修复：将 description 内容转换为 CDATA
    def fix_cdata(match):
        content = match.group(1)
        # 清理可能存在的嵌套转义
        content = content.replace('&amp;lt;', '<').replace('&amp;gt;', '>')
        content = content.replace('&lt;', '<').replace('&gt;', '>')
        content = content.replace('&amp;amp;', '&')
        return f'<content:encoded><![CDATA[{content}]]></content:encoded>'
    
    # 1. 添加 content 命名空间
    rss_xml = rss_xml.replace('<rss version="2.0">', 
                             '<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">')
    
    # 2. 替换 description 为 content:encoded with CDATA
    rss_xml = re.sub(r'<description>(.*?)</description>', fix_cdata, rss_xml, flags=re.DOTALL)
    
    # 3. 移除原来的 description 标签（如果还有残留）
    rss_xml = re.sub(r'<description>.*?</description>', '', rss_xml, flags=re.DOTALL)
    
    # 4. 确保 channel 也有 content:encoded
    if '<content:encoded>' not in rss_xml:
        rss_xml = rss_xml.replace('<description>知乎日报 RSS feed</description>', 
                                 '<content:encoded><![CDATA[知乎日报 RSS feed]]></content:encoded>')
    
    return rss_xml

if __name__ == "__main__":
    rss_content = generate_rss()
    with open('zhihu.xml', 'w', encoding='utf-8') as f:
        f.write(rss_content)
    print("RSS feed generated successfully!")