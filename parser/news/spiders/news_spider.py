import scrapy
from scrapy.http import HtmlResponse, TextResponse
from pathlib import Path
import sys
# app_path = Path(__file__).parent.resolve().parents[1]
# sys.path.insert(0, app_path)
from items import NewsItem 


class NewsSpider(scrapy.Spider):
    name = "news_spider"
    allowed_domains = ["news.am"]
    start_urls = ["https://news.am/eng/"]
    domain = "news.am"
    
    URL_TOP_NEWS_ARTICLE = "//div[@class='news-list short-top']/a[@class='news-item']/@href"
    ARTICLE_FIELDS = {
    'title': 
        [
            "//div[@class='article-title']/text()", 
            "//div[contains(@id,'opennews')]//h1/text()",
        ],
    'img': 
        [
            "//div[@class='article-text']/img/@src", 
            "//div[@id='opennewstext']/img/@src",
            "//div[@class='article-text']/iframe[contains(@src, 'youtube')]/@src"
        ],
    'text': 
        [
            "string(//span[@class='article-body'])", 
            "//div[@id='opennewstext']//*[not(self::h1 or self::div or self::img)]/text()",
        ],
    }

    def parse(self, response):
        top_news_article_urls = response.xpath(self.URL_TOP_NEWS_ARTICLE)
        for url in top_news_article_urls.extract():
            # testlogger.info(link)
            yield response.follow(url, callback=self.parse_item)

    def parse_item(self, response: HtmlResponse):

        doc_values = {field: [response.xpath(xpath).extract_first() 
            for xpath in xpathes if response.xpath(xpath).extract_first() ][0] 
            for (field, xpathes) in self.ARTICLE_FIELDS.items()}
        doc_values['url'] = response.url
        yield NewsItem(doc_values)
