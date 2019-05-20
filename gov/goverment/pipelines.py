# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import mysql.connector

class GovermentPipeline(object):
    def __init__(self):
        # 连接数据库
        self.connect = mysql.connector.connect(
            host='127.0.0.1',#数据库地址
            port=3306,# 数据库端口
            db='spider', # 数据库名
            user = 'root', # 数据库用户名
            passwd='123456', # 数据库密码
            charset='utf8', # 编码方式
            use_unicode=True)

        # 通过cursor执行增删查改
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        #数据存储到数据库中
        self.cursor.execute(
            """insert into zwgk(gw_id, url,capture_time,gw_title,theme,sub_theme,index_num,
            issue_agency,issue_number,prescription,written_date,publish_date,gw_txt_path)
            value (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",  # 纯属python操作mysql知识，不熟悉请恶补
            (item['gw_id'],  # item里面定义的字段和表字 段对应
             item['gw_url'],
             #capture_time,
             item['capture_time'],
             item['gw_title'],
             item['theme'],
             item['sub_theme'],
             item['index_num'],
             item['issue_agency'],
             item['issue_number'],
             item['prescription'],
             #written_date,
             item['written_date'],
             #publish_date,
             item['publish_date'],
             item['gw_txt_path'])
        )
        #提交mysql语句并执行
        self.connect.commit()
        #文本信息存储到txt文件中
        with open(item['gw_txt_path'],'w', encoding='utf-8') as f:
            f.write(item['gw_text'])
        return item
