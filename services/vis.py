name="Vis"
description = "For displaying videos on brzeczyszczykiewicz"
show = False

#http://twistedmatrix.com/documents/8.2.0/conch/howto/conch_client.html

class Page(PageBase):
	#subv4 = (127, 0, 0, 1)
	#mask4 = (255, 255, 255, 0)
	subv4 = map(int, Settings.conf.get("vis", "ipv4_subnet").split("."))
	maskv4 = map(int, Settings.conf.get("vis", "ipv4_mask").split("."))
	
	#todo: ipv6, if i find a way with twisted. hosting on ipv6 on linux breaks ipv4 aswell?

	usage="""<h1>Brzeczyszczykiewicz</h1>
<p>
	todo: add form with capcha here
</p>
"""

	denied = """<h1>Brzeczyszczykiewicz</h1>
<p>
	You must be on pvv's local network to use this service.
</p>
"""
	def ValidIP(self, request):
		ip = map(int, request.getClientIP().split("."))
		for i, (s, m) in enumerate(zip(self.subv4, self.maskv4)):
			if s & m <> ip[i] & m:
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

		return "Not yet implemented"
