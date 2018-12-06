# -*- coding: utf-8 -*-
import json
import codecs
from datetime import datetime
import pymysql
from twisted.enterprise import adbapi
from scrapy.mail import MailSender


class JsonPipeline(object):
    def __init__(self):
        self.file = codecs.open('results.json', 'w', encoding='utf8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii= False) + "\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()


class MySQLStorePipeline():

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            port=settings['MYSQL_PORT'],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbargs)
        return cls(dbpool)

    def __init__(self, dbpool):
        self.dbpool = dbpool

    def process_item(self, item, spider):
        d = self.dbpool.runInteraction(self._conditional_insert, item, spider)
        d.addErrback(self._handle_error, item, spider)#调用异常处理方法
        d.addBoth(lambda _: item)
        return d

    def _conditional_insert(self, conn, item, spider):
        conn.execute("insert into movies (title, rate) VALUES (%s, %s)", (item['title'], item['rate']))#movies为表名

    def _handle_error(self, failure, item, spider):
        print(failure)

class MailPipeline(object):
    def __init__(self):
        self.count = 0

    def process_item(self, item, spider):
        self.count = self.count + 1
        return item

    def close_spider(self, spider):
        mailer = MailSender(
            smtphost="smtp.163.com",  # 发送邮件的服务器
            mailfrom="xxxxx@163.com",  # 邮件发送者
            smtpuser="xxxxx",  # 用户名
            smtppass="xxxxx",  # 授权码
            smtpport=25  # 端口号
        )
        send_time = datetime.now().replace(microsecond=0).isoformat(' ')
        mail_body = send_time + str(self.count) + u""" 
        items processed successfully!
        """
        mail_subject = u'scraped.'
        mailer.send(to=["xxxxx@qq.com", "xxxxx@gmail.com"], subject=mail_subject, body=mail_body)