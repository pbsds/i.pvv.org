from twisted.web import server, resource, static
from twisted.internet import reactor, ssl
from twisted.web.util import redirectTo as TwistedRedirectTo
import os, sys, glob, __builtin__, ConfigParser, platform

class Settings:
	def __init__(self):
		if not os.path.isfile("config.ini"):
			from shutil import copy
			copy("default-config.ini", "config.ini")
			del copy#ugly
		
		self.conf = ConfigParser.ConfigParser()
		
		f = open("config.ini", "r")
		self.conf.readfp(f)
		f.close()
Settings = Settings()
class Template():
	def __init__(self):
		f = open("template/base.html", "rb")
		self.template = f.read().replace("\r\n", "\n").replace("\r", "\n")
		f.close()
		
		f = open("template/404.html", "rb")
		self.not_found = f.read().replace("\r\n", "\n").replace("\r", "\n")
		f.close()
		
		self.domain = Settings.conf.get("server", "domain")
		self.default_title = Settings.conf.get("server", "default_title")
	def MakePage(self, request, body, title=None):
		#Session = request.getSession()
		t = title if title else self.default_title
		return self.template.replace("<!--BODY-->", body).replace("<!--TITLE-->", t)
Template = Template()

class NotFound(resource.Resource):#404 page
	isLeaf = True
	def render(self, request):
		request.setResponseCode(404)
		print "%s got 404 when requesting \"%s\"" % (request.getClientIP(), request.uri)
		
		return Template.MakePage(request, Template.not_found, "404 - Not Found")
NotFound = NotFound()

class Root(resource.Resource):
	isLeaf = False
	NotFound = NotFound
	def getChild(self, name, request):
		if name == "":
			return self
		if name == "favicon.ico":
			return self.getChildWithDefault("template", request).getChildWithDefault("favicon.ico", request)
			pass
		return self.NotFound
	def render(self, request):
		request.redirect("/home")
		return Template.MakePage(request, "")
class pageBase(resource.Resource):#to be used by plugins
	Template = Template
	isLeaf = False
	NotFound = NotFound
	def getChild(self, name, request):#usually don't get called if a child exists
		if name == "":
			return self
		return self.NotFound

def LoadPlugins():
	global PageBase, Services
	#print "Loading services..."
	__builtin__.PageBase = pageBase#ugly...
	#__builtin__.Template = Template#ugly...
	__builtin__.Services = Services#ugly...
	__builtin__.Settings = Settings#ugly...
	__builtin__.reactor = reactor#Really shouldn't be neccesary, since reactor.run() does something like this....
	
	#Backup and change sys.path:
	old = sys.path[:]
	sys.path[0] = os.path.join(os.getcwd(), "services")
	
	#Load plugins:
	for i in glob.glob("services/*.py"):
		name = ".".join(os.path.split(i)[-1].split(".")[:-1])
		if name == "template": continue
		print "Loading services/%s.py..." % name
		module = __import__(name)
		Services[name] = module
		Root.putChild(name, module.Page())
	
	#Restore old sys.path:
	sys.path = old
	#print "Done!"
#/home is a service
#/template is hardcoded as a filedirectory


Root = Root()
Root.putChild('template',  static.File(os.path.join("template" ,""), "text/plain"))

#is this needed?
Services = {}#"filename" : module
LoadPlugins()

print "Server start!"
print
plat = platform.uname()[0]

#todo: add this http header:
#Access-Control-Allow-Origin: *
#(CORS HTTP)

#IPv6 breaks #breaks request.getClientIP()
#https://twistedmatrix.com/trac/ticket/7704

#todo: support multible hostnames on ssl:
#https://stackoverflow.com/questions/12149119/twisted-listenssl-virtualhosts
#contectfactory idea: read dns names from crt file.
#bash: openssl x509 -text -noout -in {crt filename}

ports = map(Settings.conf.getint, ["server"]*2, ("port", "sport"))
has_ssl = os.path.exists("server.key") and os.pat.exists("server.crt")
if plat == "Linux":
	#linux forwards IPv4 connections to "::ffff:<ipv4 address>"
	reactor.listenTCP(ports[0], server.Site(Root), interface="::")
	if has_ssl:
		#reactor.listenTCP(ports[0], server.Site(TwistedRedirectTo("https://i.pvv.org")), interface="::")
		reactor.listenSSL(ports[1], server.Site(Root), ssl.DefaultOpenSSLContextFactory("server.key", "server.crt"), interface="::")
else:#elif plat == "Windows" or plat[-3:] == "BSD":
	reactor.listenTCP(ports[0], server.Site(Root))
	reactor.listenTCP(ports[0], server.Site(Root), interface="::")#breaks request.getClientIP()
	if has_ssl:
		#reactor.listenTCP(ports[0], server.Site(TwistedRedirectTo("https://i.pvv.org")))
		#reactor.listenTCP(ports[0], server.Site(TwistedRedirectTo("https://i.pvv.org")), interface="::")
		reactor.listenSSL(ports[1], server.Site(Root), ssl.DefaultOpenSSLContextFactory("server.key", "server.crt"))
		reactor.listenSSL(ports[1], server.Site(Root), ssl.DefaultOpenSSLContextFactory("server.key", "server.crt"), interface="::")

reactor.run()












