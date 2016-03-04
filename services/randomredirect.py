from twisted.web.util import redirectTo as TwistedRedirectTo
from twisted.web.client import Agent, ResponseDone
from twisted.web.server import NOT_DONE_YET
from twisted.web.iweb import UNKNOWN_LENGTH
from twisted.web.http_headers import Headers
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.internet.ssl import ClientContextFactory
from twisted.python.failure import Failure
import random

name="Random Redirect"
description = "A random link redirector."
show = True

RESPONSE_LENGTH_LIMIT = 10 * 1024#20 kb

class ResponsePrinter(Protocol):#a dumb response reciever
	def __init__(self, finished):
		self.finished = finished
		#implement a size limit?
		self.data = []
		
	def dataReceived(self, recv):
		self.data.append(recv)
	def connectionLost(self, reason):
		#print 'Finished receiving body:', reason.getErrorMessage()
		if reason.check(ResponseDone):
			self.finished.callback("".join(self.data))
		else:
			self.finished.errback(reason)
class WebClientContextFactory(ClientContextFactory):#accepts all ssl certificates
    def getContext(self, hostname, port):
        return ClientContextFactory.getContext(self)

def is_valid_url(check):
	if check[:8] <> "https://" and check[:7] <> "http://":
		return False
	elif "." not in check[7:-1]:
		return False
	return True

class Page(PageBase):
	usage="""<h1>Random Redirect</h1>
<p>
	This is a simple service to redirect incoming requests to a random URL chosen from a list provided by the user.<br/>
	This can be used to randomize 
</p>
"""
	contextFactory = WebClientContextFactory()
	agent = Agent(reactor, contextFactory)#should i really reuse this?
	def agent_callback(self, response, request):
		#print "Response code:", response.code
		
		headers = dict(response.headers.getAllRawHeaders())
		error = None
		
		if response.code <> 200:
			error = "Return code was not 200: Recieved return code: %i" % response.code
			if response.code == 302:
				error += ". HTTP redirects are not implemented"
		elif response.length <> UNKNOWN_LENGTH and response.length > RESPONSE_LENGTH_LIMIT:
			error = "Maximum response length of %.1fKB exceeded. Response length: %i" % (float(RESPONSE_LENGTH_LIMIT)/1024, response.length)
		elif "Content-Type" in headers and True not in (i[:5] == "text/" for i in headers["Content-Type"]):
			error = "Response Content-Type not text/* based! Content-Type: %i" % " Content-Type: ".join(headers["Content-Type"])
		
		if error:
			try:
				raise RuntimeError, error
			except:
				self.response_error(Failure(), request)#hacky way? topkek
		else:
			finished = Deferred()
			finished.addCallback(self.response_success, request)
			finished.addErrback(self.response_error, request)
			
			response.deliverBody(ResponsePrinter(finished))
	def response_success(self, data, request):
		#request.write(data)
		#request.redirect("/home")
		error = None
		destination = None
		
		if data:
			#request.write(data)
			lines = tuple(i for i in data.replace("\r\n", "\n").replace("\r", "\n").split("\n") if i)
			if False in (is_valid_url(i) for i in lines):
				error = "Response contains invalid URLs!"
			else:
				destination = random.choice(lines)
		else:
			error = "The response was empty!"
		
		if not destination:
			error = "No redirect destination could be determined!"
		if error:
			try:
				raise RuntimeError, error
			except:
				self.response_error(Failure(), request)#hacky way? topkek
		else:
			request.redirect(destination)
			request.finish()
	def response_error(self, reason, request):
		#print "reason:", reason.getErrorMessage()
		request.write("Error! Something went wrong while fetching the response! \"")
		request.write(reason.getErrorMessage())
		request.write("\"")
		request.setResponseCode(409)#Conflict
		request.finish()
	def render_GET(self, request):
		#http://pastebin.com/raw/b856TNaW
		
		if "list" in request.args:
			if is_valid_url(request.args["list"][0]):
				d = self.agent.request('GET',
				                       #'http://pastebin.com/raw/Tta3FqMd',
				                       request.args["list"][0],
				                       Headers({'User-Agent': ['%s TwistedMatrix server' % self.Template.domain]}),
				                       None)
				d.addCallback(self.agent_callback, request)
				d.addErrback(self.response_error, request)
				return NOT_DONE_YET
			else:
				request.setResponseCode(409)#Conflict
				return self.Template.MakePage(request, "<>\n\tInvalid address: \"%s\"\n</p>" % request.args["list"][0])
			
		return self.Template.MakePage(request, self.usage.replace("<!--DOMAIN-->", self.Template.domain))
	def render_POST(self, request):
		if "url" in request.args:
			url = request.arg["url"][0]
			
		else:
			request.setResponseCode(409)#Conflict
		
		
		
		return "ech"












