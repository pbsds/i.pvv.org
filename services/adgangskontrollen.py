# -*- coding: utf-8 -*-
import time

name = "Adgangskontrollen Queue"
description = "For viewing adgangskontrollen's queue number"
show = True


class Image(PageBase):
	def __init__(self):
		self.image = None
		self.requested = []
	def render_GET(self, request):
		if not self.image:
			request.setResponseCode(204)
			return "none yet"
		request.setHeader("Content-Type", "image/jpeg")
		
		self.requested.append(time.time())
		while time.time() - self.requested[0] > 1:
			self.requested.pop(0)
		print time.strftime("[%H:%M:%S]"), "adgangskontrollen/image.jpg requested. (%i times this second)" % len(self.requested)
		
		return self.image
	def render_POST(self, request):
		self.image = request.args["img"][0]
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
	Here is the queue number for adgangskontrollen on Gl&oslash;shaugen
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
