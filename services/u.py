from twisted.web.util import redirectTo as TwistedRedirectTo
from twisted.internet import reactor
import random, hashlib, os

name="URL Shortener"
description = "A URL shortening service"

class Database:#subject to change
	file = "services/u/database.dat"
	def __init__(self):
		self.chars = tuple(map(chr, range(ord("a"), ord("z")+1) + range(ord("A"), ord("Z")+1) + range(ord("0"), ord("9")+1)))
		
		self.md5 = hashlib.md5()
		self.urls = {}#[name] = (url, md5(passphrase + salt), salt)
		self.databaseUpdated=False
		
		#load database
		if os.path.exists(self.file):
			f = open(self.file, "rb")
			data = map(lambda x: x.split("\t"), f.read().replace("\r\n", "\n").replace("\r", "\n").split("\n"))
			f.close()
			for name, url, hash, salt in data:
				self.urls[name] = (url, hash, salt)
		
		#self.Add("kuk", "http://google.com", "shdfkjsdf")
		
		reactor.callLater(60*5, self.AutoFlush)
	def AutoFlush(self):
		reactor.callLater(60*5, self.AutoFlush)
		self.Flush()
	def Flush(self):
		if self.databaseUpdated:
			out = []
			for name in self.urls.keys():
				url, hash, salt = self.urls[name]
				out.append("\t".join((name, url, hash, salt)))
			
			f = open(self.file, "wb")
			f.write("\n".join(out))
			f.close()
			
			self.databaseUpdated=False
			print "URL Shortener database was flushed"
	def GetVacantName(self, length=5):
		while 1:
			i = "".join((random.choice(self.chars) for _ in xrange(length)))
			if not self.Get(i):
				return i
	def Get(self, name):
		if name in self.urls:
			return self.urls[name][0]
		else:
			return None
	def Remove(self, name, passphrase=None):
		if name in self.urls:
			if self.urls[name][1]:
				if passphrase:
					self.md5.update(passphrase + self.urls[name][2])
					if self.md5.digest() == self.urls[name][1]:
						del self.urls[name]
						self.databaseUpdated=True
						return True
			else:
				if passphrase:
					return False
				else:
					del self.urls[name]
					self.databaseUpdated=True
					return True
		return False
	def Add(self, name, url, passphrase=None):
		if name not in self.urls:
			if passphrase:
				salt = "".join((random.choice(self.chars) for _ in xrange(25)))
				self.md5.update(passphrase + salt)
				hash = self.md5.digest()
			else:
				salt, hash = "", ""
			self.urls[name] = (url, hash, salt)
			self.databaseUpdated=True
			return True
		else:
			return False

class child(PageBase):
	def render(self, request):
		ID = request.path.split("/")[2]
		
		url = self.Database.Get(ID)
		if not url:
			return self.NotFound.render(request)
		else:
			return TwistedRedirectTo(url, request)

class Page(PageBase):
	Database = Database()
	child = child()
	child.Database = Database
	
	usage="""<h1>URL shortener</h1>

<!--MESSAGE-->
<form enctype="multipart/form-data" action="/u" method="POST"><p>
	<input name="form" type="hidden" value="<!--FORM-ID-->"/>
	<input name="action" type="hidden" value="add" />
	
	This is a simple service to shorten URLs<br/><br/>
	<input name="url" type="text" value="Input URL here" style="font-size: 150%; margin:20px 10px; width:100%;" maxlength="200"/><br/>
	Will be made available at http://<!--DOMAIN-->/u/<input name="name" type="text" value="<!--NAME-->" maxlength="30"/>
	<center><input type="submit" value="Create!" class="button" style="font-size: 150%;"/></center>
	<!--todo: captcha-->
</p></form>
"""
	success="""<h1>URL shortener</h1>

<p>
	Your link was successfully made here:
	<input name="url" type="text" value="http://<!--DOMAIN-->/u/<!--URL-->"  style="font-size: 150%; margin:20px 10px; width:100%;"/><br/>
</p>"""

	def getChild(self, name, request):
		if name == "":
			return self
		#return self.NotFound
		return self.child
	def MakePage(self, request, message=None):
		form = str(random.randrange(500, 500000))
		
		Session = request.getSession()
		if hasattr(Session, "u_forms_u"):#cross-site request forgery protection. not neccesary at all, but fun
			Session.u_forms_u.append(form)
		else:
			Session.u_forms_u = [form]
		
		p = self.usage.replace("<!--DOMAIN-->", self.Template.domain).replace("<!--FORM-ID-->", form).replace("<!--NAME-->", self.Database.GetVacantName())
		return self.Template.MakePage(request, p.replace("<!--MESSAGE-->", ("<p>%s</p>" % message) if message else ""))
	def render_GET(self, request):
		return self.MakePage(request)
	def render_POST(self, request):
		if "action" in request.args:
			if request.args["action"][0] == "add":
				Session = request.getSession()
				
				if "form" not in request.args or not hasattr(Session, "u_forms_u") or request.args["form"][0] not in Session.u_forms_u:
					return self.MakePage(request, "Form not served during this session, please try again.")
				
				if "url" not in request.args or "name" not in request.args:
					return self.MakePage(request, "Not enough parameters were given, please try again")
				
				url = request.args["url"][0]
				name = request.args["name"][0]
				passphrase = None#todo
				
				if not name:
					return self.MakePage(request, "Please remember to name the shortcut")
				for i in name:
					if i not in self.Database.chars:
						return self.MakePage(request, "Please enter a valid shortcut URL. Letters and numbers only")
				if url.count(".") < 1 and len(url.split(".")[-1]) >= 2:
					return self.MakePage(request, "Please enter a valid link")
				if url[:7].lower() <> "http://":
					url = "http://"+url
				
				
				if not self.Database.Add(name, url, passphrase):
					return self.MakePage(request, "The shortened URL was already taken, please try an another one")
				
				return self.Template.MakePage(request, self.success.replace("<!--DOMAIN-->", self.Template.domain).replace("<!--URL-->", name))
		

















