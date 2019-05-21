# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HebeiGovItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()


    gw_url = scrapy.Field()         #公文来源url
    capture_time = scrapy.Field()   #文件采集时间
    gw_title = scrapy.Field()       #公文标题
    theme = scrapy.Field()          #公文主题
    #sub_theme = scrapy.Field()      #公文子主题
    #index_num = scrapy.Field()      #公文索引号
    issue_agency = scrapy.Field()   #发文机关
    issue_number = scrapy.Field()   #发文字号
    gw_id = scrapy.Field()          # 公文唯一标识id
    prescription = scrapy.Field()   #时效性
    #written_date = scrapy.Field()   #成文日期
    publish_date = scrapy.Field()   #发布日期
    gw_text = scrapy.Field()        #正文
    gw_txt_path = scrapy.Field()    #正文存储路径

