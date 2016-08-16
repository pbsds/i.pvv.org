# -*- coding: utf-8 -*-
import time

name = "Adgangskontrollen Queue"
description = "For viewing adgangskontrollen's queue number"
show = True


class Image(PageBase):
	def __init__(self):
		self.image = None
		self.recieved = 0
		self.requested = []
		f = open("services/adgangskontrollen/offline.jpg", "rb")
		self.offline = f.read()
		f.close()
	def render_GET(self, request):
		if self.image and time.time() - self.recieved > 60*10:
			self.image = None
		
		request.setHeader("Content-Type", "image/jpeg")
		
		self.requested.append(time.time())
		while time.time() - self.requested[0] > 1:
			self.requested.pop(0)
		print time.strftime("[%H:%M:%S]"), "adgangskontrollen/image.jpg requested. (%i times this second)" % len(self.requested)
		
		if not self.image:
			return self.offline
		return self.image
	def render_POST(self, request):
		self.image = request.args["img"][0]
		self.recieved = time.time()
		print time.strftime("[%H:%M:%S]"), "adgangskontrollen/image.jpg posted."
class View(PageBase):#no template
	def __init__(self):
		f = open("services/adgangskontrollen/view.html", "r")
		self.page = f.read()
		f.close()
	def render(self, request):
		return self.page
Image = Image()
View = View()
		
class Page(PageBase):
	index="""<h1>Adgangskontrollen</h1>
<p>
	Her er k&oslash;nummeret til adgangskontrollen p&aring; Gl&oslash;shaugen. Venter du i k&oslash;? Kom innom PVV da vel! Her har vi kaffe og sofa rett ved adgangskontrollen!
	<center>
		<iframe src="/adgangskontrollen/view" width="640" height="360"></iframe> <br/>
		<a href="/adgangskontrollen/view" style="opacity:0.8;">View full screen</a>
	</center>
<p>
"""
	def getChild(self, name, request):
		if name.lower() == "view":
			return View
		if name.lower() == "image.jpg":
			return Image
		return PageBase.getChild(self, name, request)
	def render(self, request):
		return self.Template.MakePage(request, self.index)
