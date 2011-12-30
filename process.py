#!/usr/bin/python
#coding=utf8
'''
Get price and other info from www.amazon.cn
'''

import os,sys,subprocess,traceback,optparse
import urllib2, urllib, datetime
import re
import utils
import logging
from utils import log

#import pymongo
#`import pymongo.objectid

import socket
socket.setdefaulttimeout(8)

__author__ = "notsobad"
__date__ = "2010.12.09"
__version__ = "0.1"

def to_price(price):
	price = (price or '').replace(',','')
	try:
		price = float(price)
	except:
		pass
	return price


class Crawer():
	def __init__(self, url):
		self.url = url
		

	def open_url(self, obj=None):
		'''
		A wrapper of urllib
		'''
		if obj:
			param = urllib.urlencode(obj)
		else:
			param = None

		req = urllib2.Request(self.url, param)
		ret = ""
		try:
			r = urllib2.urlopen(req)
			ret = r.read()
		except urllib2.URLError:
			log("Error opening url")
		except:
			log("Some error happened")
			traceback.print_exc()

		return ret



# <span id="btAsinTitle" >Apple（苹果) MC374CH/A 13.3英寸笔记本电脑(酷睿2双核 2.4GHz 4G 250G  DVD刻录 内置高清摄像头  集成显卡 蓝牙2.1+EDR USB接口 重低音)</span> 
re_name= re.compile('<span\s+id="?btAsinTitle"?>(.*)</span>')

#  <td><b class="priceLarge">￥ 8,749.00</b> 
re_price = re.compile('<td><b\s+class="priceLarge">￥\s+([^<]*)</b>')

re_desc = re.compile('<div\s+class="productDescriptionWrapper">(.*)<div\s+class="emptyClear">', re.DOTALL)

class Amazon():
	
	def __init__(self, url):
		#mongo = pymongo.Connection('localhost', 27017)
		#self.trend = mongo.price.trend
		self.ret = {}
		self.url = url
	
	def get_price(self):
		c = Crawer(self.url)
		cont = c.open_url()
		now = datetime.datetime.now()
		obj = {
			'history' : [{
				'crawer_time' : now,
				'price' : to_price( utils.re_match(re_price, cont) ),
			}],
			'name' : utils.re_match(re_name, cont),
			'desc' : utils.re_match(re_desc, cont),
			'url' : self.url,
			'last_update' : now,
		}
		return obj
	
	'''
	def update_price(self, prod_info):
		cond = {'url':self.url}
		t = self.trend.find_one(cond)

		if not t:
			self.trend.save(prod_info)
			log('This url has not added yet')
			return

		t['last_update'] = prod_info['last_update']
		
		# If the price is the same as last check.
		if t['history'][-1]['price'] != prod_info['history'][0]['price']:
			t['history'].append( prod_info['history'][0] )

		self.trend.save(t)
		return
	'''

if __name__ == "__main__":
	parser = optparse.OptionParser()
	parser.add_option("--url", dest="url", help="The target url")
	parser.add_option("--notify", dest="notify", action='store_true', default=False, help="Notify me")
	parser.add_option("--lower_than", dest="lower_than", help="Alert me when the price is lower than this value")

	(options, args) = parser.parse_args()
	if options.url:
		amazon = Amazon(options.url)
		ret = amazon.get_price()
		#amazon.update_price(ret)
		if options.notify:
			now = str(datetime.datetime.now())[11:19]
			price = ret['history'][0]['price']
			cmd = 'notify-send "%(now)s" "%(price)s" -t 8000;echo "%(price)s" | festival --tts' % locals()
			os.system(cmd)

			if options.lower_than:
				lower_than = to_price(options.lower_than)
				if price <= lower_than:
					os.system('gmessage -center -nofocus -font "Sans Bold 48" "Done! Now price is %(price)s"; echo "Done! Done! Done!" | festival --tts' % locals())

		for k in ret.keys():
			print "%15s : %s" % (k, ret[k])
	else:
		parser.print_help()
		sys.exit(1)

