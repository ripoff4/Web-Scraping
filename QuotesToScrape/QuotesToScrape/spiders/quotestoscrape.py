import scrapy


class QuotestoscrapeSpider(scrapy.Spider):
    name = "quotestoscrape"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]

    def parse(self, response):
        
        container = response.xpath('//div[contains(@class,"col-md-8")]')
        quotes = container.xpath('./div[contains(@class,"quote")]')
        for quote in quotes:
            yield {
                "text": quote.xpath('./span[contains(@class,"text")]/text()').get(),
                "author":quote.xpath('./span/small/text()').getall(),
                "tags":quote.xpath('./div[contains(@class,"tag")]/a/text()').getall(),
            }
        next = response.xpath('//li[contains(@class,"next")]/a/@href').get()
        if next:
            yield response.follow(next,self.parse)
