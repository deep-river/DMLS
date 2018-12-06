# -*- coding: utf-8 -*-
import scrapy


class DmlsItem(scrapy.Item):
    title = scrapy.Field()
    rate = scrapy.Field()
    updated = scrapy.Field()
