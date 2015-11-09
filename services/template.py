#SERVICE TEMPLATE
#Page() vil be available at "http://domain/<.py filename>"

#PageBase, a class
#Template is a instance with methods to dress up a html body and handle sessions?

name = "This is displayed in /home"
description = "this aswell"

class Page(PageBase):
	def render_GET(self, request):
		return self.Template.MakePage(request, "<p>This is a template</p>")