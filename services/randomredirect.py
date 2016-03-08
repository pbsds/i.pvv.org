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

#move to config?
RESPONSE_LENGTH_LIMIT = 10 * 1024#10 kb

class ResponsePrinter(Protocol):#a dumb response reciever
	def __init__(self, finished, maxsize=1024):
		self.finished = finished
		#implement a size limit?
		self.maxsize = maxsize
		self.size = 0
		self.data = []
		
	def dataReceived(self, recv):
		self.data.append(recv)
		self.size += len(recv)
		if self.size > self.maxsize:
			self.transport.loseConnection()
	def connectionLost(self, reason):
		#print 'Finished receiving body:', reason.getErrorMessage()
		if reason.check(ResponseDone):
			self.finished.callback("".join(self.data))
		elif self.size > self.maxsize:
			self.finished.errback(Failure(RuntimeError("Response exeeded the maxsize of %iB" % self.maxsize)))
		else:
			self.finished.errback(reason)
class WebClientContextFactory(ClientContextFactory):#accepts all ssl certificates
    def getContext(self, hostname, port):
        return ClientContextFactory.getContext(self)

def is_valid_url(check):
	if check[:8] <> "https://" and check[:7] <> "http://":
		return False
	elif "." not in check.split("/")[2][:-1]:
		return False
	return True
def queryEncode(string):
	ret = []
	for i in string:
		if ord("a") <= ord(i.lower()) <= ord("z"):
			ret.append(i)
		else:
			ret.append("%%%X" % ord(i))
	return "".join(ret)
	
class Page(PageBase):
	usage="""<h1>Random Redirect</h1>
<p>
	This is a simple service to redirect incoming requests to a random URL chosen from a list linked to in the request. 
	For example: This can be used to randomize your homepage or to randomize a asset on a webpage.<br/>
</p>
	
<h2>Usage:</h2>
<p>
	Host a raw textfile with all the possible redirection urls you need, and pass a link to this list in a http GET query under the name <i><u>list</u></i>.<br/>
	<br/>
	<b>Example:</b><br/>
	Make a <a href="http://pastebin.com/b856TNaW">pastebin document</a> a paste link to the <a href="http://pastebin.com/raw/b856TNaW">raw version</a> in the text field down below and submit.
	You'll recieve a link like this:<br/>
	<a href="http://<!--DOMAIN-->/randomredirect?list=http%3A%2F%2Fpastebin%2Ecom%2Fraw%2Fb%38%35%36TNaW">http://<!--DOMAIN-->/randomredirect?list=http%3A%2F%2Fpastebin%2Ecom%2Fraw%2Fb%38%35%36TNaW</a><br/>
	<br/>
</p>
<h2>Make your own link</h2>
<p>
	<!--RETURN-->
	<form enctype="multipart/form-data" action="./randomredirect" method="POST">
		<input name="url" type="text" placeholder="Enter url to encode here" style="font-size: 150%; margin:0px 10px; margin-bottom:20px; width:65%;" maxlength="60"/> 
		<input type="submit" value="Make link!" class="button" style="font-size: 150%; width:30%;"/>
	</form>
</p>
""".replace("<!--MAXSIZE-->", "%.2fKB" % (float(RESPONSE_LENGTH_LIMIT)/1024.))



	encodeReturn="""Your URL:<br/>
	<center><input name="url" type="text" value="%s" style="font-size: 125%%; margin:0px 10px; margin-bottom:20px; width:90%%;"/></center><br/>"""
	
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
			self.response_error(Failure(RuntimeError(error)), request)
		else:
			finished = Deferred()
			finished.addCallback(self.response_success, request)
			finished.addErrback(self.response_error, request)
			
			response.deliverBody(ResponsePrinter(finished, RESPONSE_LENGTH_LIMIT))
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
		request.setHeader("Content-Type", "text/plain; charset=utf-8")
		request.finish()
	def render_GET(self, request):
		#http://pastebin.com/raw/b856TNaW
		
		if "list" in request.args:
			if is_valid_url(request.args["list"][0]):
				d = self.agent.request('GET',#todo: redirects
				                       #'http://pastebin.com/raw/Tta3FqMd',
				                       request.args["list"][0],
				                       Headers({'User-Agent': ['%s TwistedMatrix web client' % self.Template.domain]}),
				                       None)
				d.addCallback(self.agent_callback, request)
				d.addErrback(self.response_error, request)
				return NOT_DONE_YET
			else:
				request.setResponseCode(400)#Bad Request
				request.setHeader("Content-Type", "text/plain; charset=utf-8")
				return "Invalid address: \"%s\"\n" % request.args["list"][0]
			
		return self.Template.MakePage(request, self.usage.replace("<!--DOMAIN-->", self.Template.domain).replace("<!--RETURN-->", ""))
	def render_POST(self, request):
		if "url" in request.args:
			url = request.args["url"][0]
			if is_valid_url(url):
				urle = "http://%s/randomredirect?list=%s" % (self.Template.domain, queryEncode(url))
				
				return self.Template.MakePage(request, self.usage.replace("<!--DOMAIN-->", self.Template.domain).replace("<!--RETURN-->", self.encodeReturn % urle))
		
		request.setResponseCode(400)#Bad Request
		return "<h1>400 - Bad Request</h1>\n<p>\n\tPOST wwith no/invalid parameters.\n</p>"












