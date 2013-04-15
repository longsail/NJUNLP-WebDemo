#coding: utf-8
import os.path 
import pymongo
from BaseHandler import BaseHandler

import tornado.web 
import tornado.httpserver
import tornado.ioloop 
import tornado.options

from tornado.options import define,options
define("port",default=8000,help="run on the given port",type=int)

class IndexHandler(BaseHandler):
	def get(self):
		inputText = self.get_argument('inputText','nanjing')
		project = self.get_argument('project','SMT')
		ip = self.request.remote_ip
                
		output = self.SelService(inputText,project,ip)
		self.render('index.html',output = output)

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [(r'/',IndexHandler)]
		settings = dict(
			template_path = os.path.join(os.path.dirname(__file__),"templates"),
			static_path = os.path.join(os.path.dirname(__file__),"static"),
			debug = True,
			)
		conn = pymongo.Connection("localhost",27017)
		self.db = conn["test"]
		tornado.web.Application.__init__(self,handlers,**settings)


def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application(),xheaders=True)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
