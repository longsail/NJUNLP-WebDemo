#coding: utf-8
import os.path 
import re

import tornado.web 
import tornado.httpserver
import tornado.ioloop 
import tornado.options

from  suds.client import Client

from tornado.options import define,options

define("port",default=8000,help="run on the given port",type=int)

class baseHandler(tornado.web.RequestHandler):
	def Regex(self,text):
		regex = r'[\r]?\n'
		reobj = re.compile(regex)
		return reobj.sub('',text)
				
	def CHISegWebService(self,text):
		CHISegUrl = 'http://114.212.189.224:9444/WCFICTCLASService?wsdl'
		CHISegClient = Client(CHISegUrl)

		text = self.Regex(text)
		return CHISegClient.service.RunICTCLASSegment(text)

	def SMTWebService(self,text):
		SMTUrl = 'http://114.212.189.224:9000/NJUPhraZTranslationService/service?wsdl'
		SMTClient = Client(SMTUrl)

		text = self.Regex(text)
		text = self.CHISegWebService(text)
		return SMTClient.service.Translate(text)

class SmtHandler(baseHandler):

	def get(self):
		inputText = self.get_argument('inputText','nanjing')
		transOutput = self.SMTWebService(inputText)
		self.render('index.html',output = transOutput)

class ChiSegHandler(baseHandler):

	def get(self):
		inputText = self.get_argument('inputText','nanjing')
		chinSegOutput = self.CHISegWebService(inputText)
		self.render('index.html',output = chinSegOutput)


if __name__ == "__main__":
	tornado.options.parse_command_line()
	app=tornado.web.Application(
			handlers=[(r'/',SmtHandler)
				#(r'/',ChiSegHandler)
			],
			template_path=os.path.join(os.path.dirname(__file__),"templates"),
			static_path=os.path.join(os.path.dirname(__file__),"static"),
			debug=True
			)
	http_server=tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
