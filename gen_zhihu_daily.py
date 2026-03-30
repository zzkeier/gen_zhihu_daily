import requests
import datetime
import re
import html

# 获取知乎日报最新列表
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

# 从 HTML 正文提取纯文本摘要（最多 200 字）
def extract_summary(html_body, max_length=200):
    # 移除所有 HTML 标签
    text = re.sub(r'<[^>]+>', '', html_body)
    # 移除多余空白字符
    text = re.sub(r'\s+', ' ', text).strip()
    # 截取指定长度
    if len(text) > max_length:
        text = text[:max_length] + '…'
    # 转义 XML 特殊字符（避免破坏 RSS 结构）
    return html.escape(text)

# 生成 RSS XML
def generate_rss():
    news_data = get_zhihu_news()
    items_xml = []

    for story in news_data.get('stories', []):
        try:
            detail = get_news_detail(story['id'])
            title = detail.get('title', '')
            body = detail.get('body', '')
            image = detail.get('image', '')
            share_url = detail.get('share_url', '')

            if not title or not body:
                continue

            # 构建完整 HTML 正文（包含题图）
            full_html = f'<div class="main-img" style="margin-bottom: 20px;"><img src="{image}" style="max-width:100%; border-radius: 8px;"></div>' + body

            # 提取纯文本摘要
            summary = extract_summary(body)

            # 构建单个 item 的 XML
            item = f"""
            <item>
                <title>{html.escape(title)}</title>
                <link>{share_url}</link>
                <description>{summary}</description>
                <content:encoded><![CDATA[{full_html}]]></content:encoded>
                <guid isPermaLink="true">{share_url}</guid>
                <pubDate>{datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
            </item>
            """
            items_xml.append(item)
        except Exception as e:
            print(f"Error processing story {story.get('id', 'unknown')}: {e}")
            continue

    # 构建完整 RSS
    rss_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
    <channel>
        <title>知乎日报</title>
        <link>https://daily.zhihu.com/</link>
        <description>知乎日报 RSS feed</description>
        <lastBuildDate>{datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>
        <generator>Custom RSS Generator</generator>
        {''.join(items_xml)}
    </channel>
</rss>"""

    return rss_xml

if __name__ == "__main__":
    rss_content = generate_rss()
    with open('zhihu.xml', 'w', encoding='utf-8') as f:
        f.write(rss_content)
    print("RSS feed generated successfully!")
