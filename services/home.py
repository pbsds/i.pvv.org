name = "ignored"
description = "ignored"

class Page(PageBase):
	body_base = """<h1><!--DOMAIN--> services:</h1>
<table>
	<!--items-->
</table>"""

	item_base = """<tr>
		<td style="text-align: right;"><a href="/%s"><b>%s</b></a></td>
		<td>%s</td>
	</tr>"""

	def render_GET(self, request):
		items = []
		for i in Services.keys():
			if i == "home": continue
			n = Services[i].name if hasattr(Services[i], "name") else i
			d = " - <i>%s</i>" %Services[i].description if hasattr(Services[i], "description") else ""
			items.append(self.item_base % (i, n, d))
		
		return self.Template.MakePage(request, self.body_base.replace("<!--items-->", "\n\t".join(items)).replace("<!--DOMAIN-->", self.Template.domain))