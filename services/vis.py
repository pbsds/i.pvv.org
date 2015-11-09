name="Vis"
description = "For displaying videos on brzeczyszczykiewicz"

class Page(PageBase):
	#maskv4 = (129, 241, 210)#ipv6?
	maskv4 = (127,0,0)#ipv6?
	usage="""<h1>Brzeczyszczykiewicz</h1>
<p>
	todo: add form with capcha here
</p>
"""
	
	denied = """<h1>Brzeczyszczykiewicz</h1>
<p>
	You must be on pvv's network to use this service.
</p>
"""
	def ValidIP(self, request):
		ip = map(int, request.getClientIP().split("."))
		for i, m in enumerate(self.maskv4):
			if m <> ip[i]:
				request.setResponseCode(403)
				return False
		return True
	def render_GET(self, request):
		if not self.ValidIP(request):
			return self.Template.MakePage(request, self.denied)
		return self.Template.MakePage(request, self.usage.replace("<!--DOMAIN-->", self.Template.domain))
	def render_POST(self, request):
		if not self.ValidIP(request):
			return self.Template.MakePage(request, self.denied)
		
		return ""
