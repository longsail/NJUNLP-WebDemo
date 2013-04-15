#coding: utf-8
import re
from suds.client import Client

import tornado.web 

class BaseHandler(tornado.web.RequestHandler):

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
				return result["target"]+result["ip"]
			else:
				output = self.SMTWebService(text)
				SMTResult = self.saveResult(text,output,ip)
				collsmt.insert(SMTResult)

				return SMTResult["target"]+SMTResult["ip"]
			
		elif project == "SEG": 
			result = collseg.find_one({"source":text})
			if result:
				return result["target"]+result["ip"]
			else:
				output = self.CHISegWebService(text)
				SEGResult = self.saveResult(text,output,ip)
				collseg.insert(SEGResult)

				return SEGResult["target"]+SEGResult["ip"]
		else:
			output = "longsail Love Nju\n"+"longsail"
			return output+ip
