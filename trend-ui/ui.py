#!/usr/bin/python
#coding=utf-8
import web
import pdb, traceback
import pymongo
import pymongo.objectid
import copy
import pprint
import simplejson
import time
import datetime
import os

from jinja2 import Environment,FileSystemLoader


def render_template(template_name, **context):
	extensions = context.pop('extensions', [])
	globals = context.pop('globals', {})

	jinja_env = Environment(
			loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
			extensions=extensions,
			)
	jinja_env.globals.update(globals)
	return jinja_env.get_template(template_name).render(context)

urls = (
		'/', 'index',
	)
web.config.debug = True
app = web.application(urls, globals())


if web.config.get('_session') is None:
	session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'secret':''})
	web.config._session = session
else:
	session = web.config._session

render = web.template.render('.')

class myStaticMiddleware(web.httpserver.StaticMiddleware):
    """WSGI middleware for serving static files."""
    def __init__(self, app, prefix='/media/'):
		web.httpserver.StaticMiddleware.__init__(self, app, "/media/")

def to_price(price):
	price = (price or '').replace(',','')
	try:
		price = float(price)
	except:
		pass
	return price

class PriceTrend:
	def __init__(self):
		mongo = pymongo.Connection('localhost', 27017)
		self.trend = mongo.price.trend
	def get_price(self, url):
		t = self.trend.find_one({'url': url})
		if not url:
			return None
		history = t['history']
		history.append({'price':history[-1]['price'], 'crawer_time':datetime.datetime.now() })
		history = [ {'price': to_price(h['price']), 'crawer_time': str(h['crawer_time']) } for h in history ]

		self.prod_info = {'name': t['name'], 'url':t['url'], 'last_update':str(t['last_update'])}
		return history
	
class index:
	def GET(self):
		price = PriceTrend()
		history = price.get_price('http://www.amazon.cn/Apple-%E8%8B%B9%E6%9E%9C-MC700CH-A-13-3%E8%8B%B1%E5%AF%B8%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91/dp/B004PYEGE8/ref=sr_1_1?s=pc&ie=UTF8&qid=1309341477&sr=1-1')
		return render_template('index.html', history=simplejson.dumps(history), prod_info=simplejson.dumps(price.prod_info))

if __name__ == '__main__':
	app.run(myStaticMiddleware)
