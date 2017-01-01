#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest
from scrapy.exceptions import CloseSpider

from jdspider.items import JdspiderItem
from jdspider.constants import HEADER


class JingdongSpider(CrawlSpider):
    name = "jingdong"
    allowed_domains = ["jd.com"]
    start_urls = (
        'https://www.jd.com/',
    )
    #scrapy crawl jingdong -o test.csv

    def start_requests(self):
        """
        请求商品主页，获取评论数
        """
        return [Request(
            'https://list.jd.com/list.html?cat=9987,653,655',
            #meta={'proxy':'https://124.88.67.17:843'},
            callback=self.get_rate_num,
            dont_filter=True,
        )]
    
    def get_item_list(self, response):
        """
        请求手机列表页面
        总是被重定向，还没解决，不过第一页就有60款手机，几百万条评价也够用了
        """
        page_num = response.xpath(
            '//*[@id="J_bottomPage"]/span[2]/em[1]/b/text()'
        ).extract()
        page_num = int(page_num[0])
        #print page_num
        
        for i in range(1, page_num):
            list_url = 'https://list.jd.com/list.html?cat=9987,653,655&page=%d&trans=1&JL=6_0_0' % i
            yield Request(
                list_url,
                meta={'dont_redirect':True},
                callback=self.get_items
            )
            
    def get_items(self, response):
        """
        获取商品id, 构造连接请求评论页
        """
        #from scrapy.shell import inspect_response
        #inspect_response(response, self)
        item_ids = response.xpath(
            '//*[@id="plist"]/ul/li/div/@data-sku'
        ).extract()
        #print item_ids
        
        for item_id in item_ids:
            complete_url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment&productId=%s&score=0&sortType=6&page=0&pageSize=10' % item_id
            print complete_url
            yield Request(
                complete_url,
                callback=self.get_rate_num,
            )
            
            #item_id = JdspiderItem(item_id=item_id)
            #yield item_id
        
    def get_rate_num(self, response):
        """
        获取评论数，请求评论页
        score=1为差评
        score=3为好评
        """
        #from scrapy.shell import inspect_response
        #inspect_response(response, self)
        '''
        body = response.body.decode('gb18030').encode('utf-8')
        rates = re.findall('fetchJSON_comment\((.*)\)\;', body)[0]
        jrs = json.loads(rates)
        rate_summary = jrs["productCommentSummary"]
        item_id = rate_summary["skuId"]
        '''
        #good comments
        score = 3
        # if score==1:
            # rate_num = int(rate_summary["poorCount"])
        # else:
            # rate_num = int(rate_summary["goodCount"])
        # print rate_num
        item_id = '2967927'
        
        for i in range(0, 20000):    #rate_num/10):
            rates_url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment&productId=%s&score=%d&sortType=5&page=%d&pageSize=10' % (item_id, score, i)
            yield Request(
                rates_url,
                headers=HEADER,
                callback=self.rate_parse,
            )

    
    
    def rate_parse(self, response):
        
        body = response.body.decode('gb18030').encode('utf-8')
        if body:
            rates = re.findall('fetchJSON_comment\((.*)\)\;', body)[0]
            jrs = json.loads(rates)
            jratelist = jrs["comments"]
            for i in range(10):
                rate = jratelist[i]
                item = JdspiderItem(
                    content = rate["content"]
                    ) 
                yield item
        else:
            raise CloseSpider('spider was banned')
