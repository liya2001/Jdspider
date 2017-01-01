#!/usr/bin/env python
# -*- coding: utf-8 -*-


import random  
import socket  
import struct

from jdspider.settings import USER_AGENT

HEADER = {
    'Host': 'club.jd.com',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'max-age=0',
    'Accept': '*/*',
    'Origin': 'https://www.jd.com',
    'X-Requested-With': 'XMLHttpRequest',
    'x-forwarded-for': socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))),
    'User-Agent': USER_AGENT,
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
}

