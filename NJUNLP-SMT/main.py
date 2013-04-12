#coding: utf-8
import os.path 
import re
from suds.client import Client
import pymongo
#from time import time

import tornado.web 
import tornado.httpserver
import tornado.ioloop 
import tornado.options

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

	def saveResult(self,text,output,ip):
		result = dict()

		result["source"] = text
		result["target"] = output
		result["ip"] = ip

		return result

	def SelService(self,text,project,ip):
		collsmt = self.application.db.testsmt
		collseg = self.application.db.testseg

		if project == "SMT":
			result =  collsmt.find_one({"source":text})
			if result:
				return result["target"]
			else:
				output = self.SMTWebService(text)
				SMTResult = self.saveResult(text,output,ip)
				collsmt.insert(SMTResult)

				return output
			
		elif project == "SEG": 
			result = collseg.find_one({"source":text})
			if result:
				return result["target"]
			else:
				output = self.CHISegWebService(text)
				SEGResult = self.saveResult(text,output,ip)
				collseg.insert(SEGResult)

				return output
		else:
			return "longsail Love Nju"

class IndexHandler(baseHandler):
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
