import requests
import PyRSS2Gen
import datetime
import html

def generate_zhihu_rss():
    base_api = "https://news-at.zhihu.com/api/3/news/"
    
    latest_response = requests.get(base_api + "latest")
    latest_response.encoding = "utf-8"
    stories = latest_response.json().get("stories", [])
    
    rss_items = []
    for story in stories:
        try:
            title = story["title"]
            url = story["url"]
            story_id = url.split("/")[-1]
            
            detail_response = requests.get(base_api + story_id)
            detail_response.encoding = "utf-8"
            detail_data = detail_response.json()
            body = html.unescape(detail_data.get("body", ""))
            description = f"<![CDATA[{body}]]>"
            
            rss_items.append(
                PyRSS2Gen.RSSItem(
                    title=title,
                    link=url,
                    description=description,
                    pubDate=datetime.datetime.utcnow()
                )
            )
        except Exception as e:
            print(f"处理失败: {e}")
    
    rss = PyRSS2Gen.RSS2(
        title="知乎日报",
        link="https://www.zhihu.com/",
        description="知乎日报全文RSS。",
        lastBuildDate=datetime.datetime.utcnow(),
        items=rss_items
    )
    xml_content = rss.to_xml(encoding="utf-8")
    with open("zhihu.xml", "w", encoding="utf-8") as f:
        f.write(xml_content)

if __name__ == "__main__":
    generate_zhihu_rss()