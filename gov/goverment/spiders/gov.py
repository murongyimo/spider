# -*- coding: utf-8 -*-
import scrapy
import json
import  requests
import datetime
import time
from goverment.items import GovermentItem

# log_time = datetime.datetime.now()
#  log_file_path = "log/zfgw{}.{} {}:{}.log".format(log_time.month,log_time.day,log_time.hour,log_time.minute)
# logging.basicConfig(filename=log_file_path,level=logging.DEBUG)
gw_base_path = "gov_text/"
cato_base_url = "http://sousuo.gov.cn/data?t=zhengce_gw&q=&timetype=timeqb&mintime=&maxtime=&sort=pubtime&sortType=1&searchfield=&pcodeJiguan=&childtype=&subchildtype=%s&tsbq=&pubtimeyear=&puborg=&pcodeYear=&pcodeNum=&filetype=&"

headers = {
   'Accept': '*/*',
    'Accept-Encoding':'gzip, deflate',
    'X-Requested-With':'XMLHttpRequest',
   'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
}


class GovSpider(scrapy.Spider):
    name = 'gov'
    start_urls = ['http://sousuo.gov.cn/s.htm?t=zhengce']
    # 爬虫请求搜索网站，得到response，传入parse

    def parse(self, response):
        themes = response.css(' .dys_policySearchResultsPage_left.fl>h5:nth-child(4)+div ul:first-child>li')
        # theme:22个大标题+小标题
        for i in range(len(themes)):
            theme = themes.css('li.dys_classified_by_subject_nav_item>a::text').re('(.+)\(\d+\)')[i]
            # theme: 提取大标题
            sub_themes_a = themes[i].css('li.dys_classified_by_subject_nav_item ul a')
            # sub_themes: 提取所有的子标题所在的<a>标签
            # 以下开始循环子标题
            for j in range(len(sub_themes_a)):
                # 分别获取所有子主题的标签名、用于获取json的type
                sub_theme = sub_themes_a.css('::text').re('(.+)\(\d+\)')[j]
                sub_theme_type = sub_themes_a[j].css('::attr(type)').extract_first()
                # catalo_start_url:获取sub_theme即子标签点击后返回的json文件
                catalo_start_url = cato_base_url % sub_theme_type
                print("【catalo_start_url】:"+catalo_start_url)
                time.sleep(3)
                res = requests.get(catalo_start_url + "p=0&n=5&inpro=",headers=headers)
                #yield scrapy.Request(catalo_start_url, callback=self.start_parse,
                #meta={'theme': theme, 'sub_theme': sub_theme})
                context = json.loads(res.text)
                # totalpage:int类型，记录总页数
                totalpage = context["searchVO"]["totalpage"]
                print("totalpage : %d" % totalpage)
                for cnt in range(totalpage):
                    # 构造每一页的url
                    catalo_url = catalo_start_url + "p=%d&n=5&inpro=" % cnt
                    yield scrapy.Request(catalo_url, callback=self.page_parse,
                                         meta={'theme': theme, 'sub_theme': sub_theme})
                    # res = requests.get(catalo_url)

                    ######################以下测试用#####################
                    # print(theme + sub_theme + "summary:" + gw['summary'])
                    #break
                print("sub_theme:" + sub_theme, "sub_them_type:" + sub_theme_type)
                #break
            print(theme)
            #break

    def start_parse(self,response):

        pass

    def page_parse(self, response):
        context = json.loads(response.body)
        gws = context["searchVO"]["listVO"]
        meta = response.meta
        for gw in gws:
            # gw['url']当中存储了当前页面到公文页面的链接,访问url，获取公文网站，再进行爬取处理
            gw_url = gw['url']
            print("gw_url:",gw_url)
            yield scrapy.Request(gw_url, callback=self.gw_parse, meta={'gw_url': gw_url, 'theme': meta['theme'],
                                                                       'sub_theme': meta['sub_theme']})
            #break

    def gw_parse(self, response):

        item = GovermentItem()
        #文件标识id，由索引号转化而来
        item['gw_id']= ''.join(response.css('.wrap .bd1:first-child tr:nth-child(1)>td:nth-child(2)::text').re('(.+)/(.+)-(.+)'))
        #url
        item['gw_url'] = response.meta['gw_url']
        #文件采集时间
        item['capture_time'] = datetime.datetime.now()
        # 公文/新闻标题
        item['gw_title'] = response.css('.wrap .bd1:first-child tr:nth-child(3)>td:nth-child(2)::text').extract_first()
        #文件主题类别
        item['theme'] = response.meta['theme']
        #文件细分主题类别
        item['sub_theme'] = response.meta['sub_theme']
        #索引号
        item['index_num'] = response.css('.wrap .bd1:first-child tr:nth-child(1)>td:nth-child(2)::text').extract_first()
        #发文机关
        item['issue_agency'] = response.css('.wrap .bd1:first-child tr:nth-child(2)>td:nth-child(2)::text').extract_first()
        #发文字号
        item['issue_number'] = response.css('.wrap .bd1:first-child tr:nth-child(4)>td:nth-child(2)::text').extract_first()
        #时效性,默认为1，即有效。当时效性字段非空时，证明文件失效，则值为0
        prescription_text = response.css('.wrap .bd1:nth-child(2) td:nth-child(4) span::text').extract_first()
        item['prescription'] = 1
        if prescription_text is not None:
            item['prescription'] = 0
        #成文日期
        item['written_date'] = datetime.datetime.strptime(\
            response.css('.wrap .bd1:first-child tr:nth-child(2)>td:nth-child(4)::text').extract_first(), "%Y年%m月%d日")
        #发布日期
        item['publish_date'] = datetime.datetime.strptime(\
            response.css('.wrap .bd1:first-child tr:nth-child(4)>td:nth-child(4)::text').extract_first(), "%Y年%m月%d日")
        #文件采集时间
        # item['capture_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #正文,去除\n,\r,\t,\u3000,\xa0,包含题目、字体、
        text = response.css('.wrap>table:nth-child(3) span ::text,p ::text').extract()
        move = dict.fromkeys((ord(c) for c in u"\u3000\xa0\t\r\n"))
        item['gw_text'] = "".join(text).translate(move)
        #gw_txt_path:txt文件存储路径
        item['gw_txt_path'] = gw_base_path + "gov_"+item['gw_id']+".txt"
        yield item

