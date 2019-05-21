# -*- coding: utf-8 -*-
import scrapy
from heBei_gov.items import HebeiGovItem
import datetime
gw_base_path = "hebei_text/"

class HebeiGovSpider(scrapy.Spider):
    name = 'hebei_gov'
    allowed_domains = ['hebei.gov.cn']
    start_urls = ['http://info.hebei.gov.cn/eportal/ui?pageId=6817578']

    def parse(self, response):
        #存储所有主题的<a>标签
        themes_a = response.css('.zcwjw1200>div:first-child>div:nth-child(4) a')
        #存储所有的主题文字内容
        themes = themes_a.css('::text').extract()
        #存储所有的初始链接
        #start_urls=themes_a.css('::attr(href)').extract()
        for i in range(len(themes_a)):
            #循环处理每个主题，进入start_url中
            # print("【theme】"+themes[i])
            yield response.follow(themes_a[i],callback=self.theme_parse,meta={'theme':themes[i]})
            #totapage=response.css('.easysite-total-page b::text').extract()[3]


    def theme_parse(self,response):
        #函数对每个主题中进行处理，response.meta[theme]中存储主题内容
        #提取正文url list
        urls=response.css('.zcwjw1200>div:nth-child(2) tbody>tr:first-child a::attr(href)').extract()
        for url in urls:
            yield response.follow(url,callback=self.gw_parse,meta={'theme':response.meta['theme']})
        #存储下一页相对url
        next_page=response.css('.easysite-page-wrap>a:nth-child(3)::attr(tagname)').extract_first()
        #处理每一页内容
        if next_page is not None:
            yield response.follow(next_page,callback=self.theme_parse,meta={'theme':response.meta['theme']})


    def gw_parse(self,response):
        item = HebeiGovItem()
        item['gw_url'] = response.url
        item['capture_time'] = datetime.datetime.now()
        item['gw_title'] = response.css('.xxgk_bmxl tr:nth-child(1)>td:nth-child(2)::text').extract_first()
        item['theme'] = response.meta['theme']
        # item['sub_theme']
        # item['index_num']
        item['issue_agency'] = response.css('.xxgk_bmxl tr:nth-child(1)>td:nth-child(4)::text').extract_first()
        item['issue_number'] = response.css('.xxgk_bmxl tr:nth-child(2)>td:nth-child(2)::text').extract_first()
        # item['gw_id'] ='_'.join(
        #     response.css('.xxgk_bmxl tr:nth-child(2)>td:nth-child(2)::text').re('(.*)[\[〔](.*)[\]〕](.*)号')
        # )
        item['gw_id'] =item['issue_number']
        item['prescription'] = 1
        # item['written_date'] = datetime.datetime.strptime( )
        item['publish_date'] = datetime.datetime.strptime(
            response.css('.xxgk_bmxl tr:nth-child(2)>td:nth-child(4)::text').extract_first(), "%Y年%m月%d日"
        )
        move = dict.fromkeys((ord(c) for c in u"\u3000\xa0\t\r\n"))
        text = response.css('.article_tit+div ::text').extract()
        item['gw_text'] = ''.join(text).translate(move)
        item['gw_txt_path'] = gw_base_path + "hb_" + item['gw_id'] + ".txt"
        yield item