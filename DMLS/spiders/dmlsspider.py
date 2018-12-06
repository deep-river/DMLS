import scrapy
from ..items import DmlsItem
from datetime import datetime

class dmlsspider(scrapy.Spider):
    name = 'dmls'
    allowed_domains = ["douban.com"]
    start_urls = [
        "https://www.douban.com/doulist/240612/"
    ]

    def parse(self, response):
        items =[]
        for info in response.xpath('//div[@class="bd doulist-subject"]'):
            item = DmlsItem()
            item['title'] = info.xpath('div[@class="title"]/a/text()').extract()
            item['rate'] = info.xpath('div[@class="rating"]/span[@class="rating_nums"]/text()').extract()
            item['updated'] = datetime.now().replace(microsecond=0).isoformat(' ')
            items.append(item)
            yield item

            next_page = response.xpath('//span[@class="next"]/a/@href')
            if next_page:
                url = response.urljoin(next_page[0].extract())
                yield scrapy.Request(url, self.parse)