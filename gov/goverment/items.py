# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GovermentItem(scrapy.Item):
    gw_id = scrapy.Field()
    gw_url = scrapy.Field()
    capture_time = scrapy.Field()
    gw_title = scrapy.Field()
    theme = scrapy.Field()
    sub_theme = scrapy.Field()
    index_num = scrapy.Field()
    issue_agency = scrapy.Field()
    issue_number = scrapy.Field()
    prescription = scrapy.Field()
    written_date = scrapy.Field()
    publish_date = scrapy.Field()
    gw_text = scrapy.Field()
    gw_txt_path = scrapy.Field()