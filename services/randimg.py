from twisted.web.util import redirectTo as TwistedRedirectTo
import random

name="RandIMG"
description = "A random imgur image link redirector"
show = False

class Page(PageBase):
	usage="""<h1>RandIMG</h1>
<p>
	This is a simple service to redirect requests to a random image hosted on <a href="http://imgur.com/">imgur.com</a> within a selection chosen by the user.<br/>
	I made this to randomize my 4chan mascots on each pageload when using <a href="https://userstyles.org/styles/85301/minmascot-for-4chan">MinMascot for 4chan</a>.<br/>
</p>
<h3>Usage:</h3>
<p>
	Let's say i want to use these three images:<br/>
	<a href="http://i.imgur.com/W2Wawkj.png">http://i.imgur.com/<b>W2Wawkj</b>.png</a><br/>
	<a href="http://i.imgur.com/6NdaXaP.png">http://i.imgur.com/<b>6NdaXaP</b>.png</a><br/>
	<a href="http://i.imgur.com/3u7cTw3.png">http://i.imgur.com/<b>3u7cTw3</b>.png</a><br/>
	<br/>
	Extract the ID's:<br/>
	<b>W2Wawkj</b><br/>
	<b>6NdaXaP</b><br/>
	<b>3u7cTw3</b><br/>
	<br/>
	And encode them either as http GET or POST parameters, like this (GET):<br/>
	<a href="http://<!--DOMAIN-->/randimg?img=W2Wawkj&img=6NdaXaP&img=3u7cTw3">http://<!--DOMAIN-->/randimg?img=<b>W2Wawkj</b>&img=<b>6NdaXaP</b>&img=<b>3u7cTw3</b></a><br/>
</p>

"""
	
	def render(self, request):
		if "img" in request.args:
			return TwistedRedirectTo("http://i.imgur.com/%s.png" % random.choice(request.args["img"]), request)
		elif request.method.lower() in ("get", "head"):
			return self.Template.MakePage(request, self.usage.replace("<!--DOMAIN-->", self.Template.domain))
		return ""