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

class IndexHandler(tornado.web.RequestHandler):
	def ChiToEngTranslate(self,text):
		WordSegUrl = 'http://114.212.189.224:9444/WCFICTCLASService?wsdl'
		WordSegClient = Client(WordSegUrl)

		SMTUrl = 'http://114.212.189.224:9000/NJUPhraZTranslationService/service?wsdl'
		SMTClient = Client(SMTUrl)

		ChiString = WordSegClient.service.RunICTCLASSegment(text)
		EngTranString = SMTClient.service.Translate(ChiString)
		return EngTranString
	def SMTRegex(self,text):
		regex = r'[\r]?\n'
		reobj = re.compile(regex)
		text = reobj.sub('',text)
		return text

	def get(self):
		InputText = self.get_argument('InputText',"nanjing")
		InputText = self.SMTRegex(InputText)
		TransOutput = self.ChiToEngTranslate(InputText)
		self.render('index.html',TransOutput = TransOutput)

if __name__ == "__main__":
	tornado.options.parse_command_line()
	app=tornado.web.Application(
			handlers=[(r'/',IndexHandler)
			],
			template_path=os.path.join(os.path.dirname(__file__),"templates"),
			static_path=os.path.join(os.path.dirname(__file__),"static"),
			debug=True
			)
	http_server=tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
