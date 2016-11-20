#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest

#from taobao.constants import HEADER
from jdspider.items import JdspiderItem


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
            callback=self.get_item_list,
            dont_filter=True,
        )]
    
    def get_item_list(self, response):
        """
        请求手机列表页面
        """
        page_num = response.xpath(
            '//*[@id="J_bottomPage"]/span[2]/em[1]/b/text()'
        ).extract()
        page_num = int(page_num[0])
        print page_num
        
        for i in range(1, 2):
            list_url = 'https://list.jd.com/list.html?cat=9987,653,655&page=%d&trans=1&JL=6_0_0#J_main' % i
            yield Request(
                list_url,
                callback=self.get_items
            )
            
    def get_items(self, response):
        """
        获取商品id, 构造连接请求评论页，以获取评论数
        """
        #from scrapy.shell import inspect_response
        #inspect_response(response, self)
        #//*[@id="plist"]/ul/li[60]
        item_ids = response.xpath(
            '//*[@id="plist"]/ul/li/div/@data-sku'
        ).extract()
        print item_ids
        
        for i in range(10):
            item_id = item_ids[i]
            complete_url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment&productId=%s&score=0&sortType=6&page=0&pageSize=10' % item_id
            print complete_url
            yield Request(
                complete_url,
                callback=self.get_rate_num,
            )
            
            item_id = JdspiderItem(item_id=item_id)
            yield item_id
        
    def get_rate_num(self, response):
        """
        获取评论数，请求评论页
        score=1为差评
        """
        body = response.body.decode('gb18030').encode('utf-8')
        # res = Selector(response).xpath('//text()')
        rates = re.findall('fetchJSON_comment\((.*)\)\;', body)[0]
        jrs = json.loads(rates)
        rate_summary = jrs["productCommentSummary"]
        print type(rate_summary)
        poorate_num = int(rate_summary["poorCount"])
        item_id = rate_summary["skuId"]
        print item_id
        print poorate_num
        
        for i in range(2):
            rates_url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment&productId=%s&score=1&sortType=5&page=%d&pageSize=10' % (item_id, i)
            yield Request(
                rates_url,
                callback=self.rate_parse,
                #dont_filter=True,
            )

    
    
    def rate_parse(self, response):
        
        body = response.body.decode('gb18030').encode('utf-8')
        # res = Selector(response).xpath('//text()')
        rates = re.findall('fetchJSON_comment\((.*)\)\;', body)[0]
        #print rates
        print type(rates)
        jrs = json.loads(rates)
        #jrs = rates[0]
        print type(jrs)
        jratelist = jrs["comments"]
        for i in range(10):
            rate = jratelist[i]
            item = JdspiderItem(
                content = rate["content"]
                ) 
            yield item
        #每次yield item之后都请求一次？
            
    
