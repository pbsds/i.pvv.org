name="Custom DNS"
description = "For redirecting traffic to certain addresses"
show = False

#helpers:
f = open("services/dns/banned.txt", "rt")
BANNED = set(i for i in f.read().split("\n") if i)
f.close()
del f

def isBanned(domain):
	#speed:
	b = BANNED
	
	names = domain.split(".")
	for i in range(len(names), 0, -1):
		if ".".join(names[-i:]) in b:
			return True
	return False
def isValidDomainName(domain):#intentionally won't accept toplevel domains alone
	if len(domain) > 63:
		return False
	if "." not in domain:
		return False
	if len(domains.split(".")[-1]) < 2:
		return False
	for i in domain:
		if not (ord("a") <= ord(i.lower()) <= ord("z")) and i != "-":
			return False
	return True
def isValidIPv4(address):
	if len(address) > 15:
		return False
	n = address.split(".")
	if len(n) != 4:
		return False
	if False in (i.isdigit() for i in n):
		return False
	if True in (int(i) >= 256 for i in n):
		return False
	return True
def isValidIPv6(address):#should a address like "ffff::127.0.0.1" legal?
	for i in address:
		if i.lower() not in "0123456789abcdef:":
			return False
	if address.count("::") > 1:
		return False
	n = 0
	for part in address.split("::"):
		for i in part.split(":"):
			if len(i) > 4:
				return False
		n += part.count(":")+1
	if n > 8:
		return False
	return True
	
class Page(PageBase):
	usage="""<h1>Custom DNS</h1>
<center><p>
	<b><i><u>Warning: To no set this DNS server for normal daily use, it'll probably be filled malicious entries!</u></i></b><br/>
</p></center>
<p>
	
	This is a DNS server intended mainly for reverse-engeneering purposes. You can add your own overides for certain addresses, but some of the most popular domain names are banned due of the potential risks a public custom DNS server could contain. Click here to view all banned domains: TODO
</p>
"""
	def render_GET(self, request):
		return "WIP"
		pass
		return self.Template.MakePage(request, self.usage.replace("<!--DOMAIN-->", self.Template.domain))
	def render_POST(self, request):
		
		return "WIP"

		
#class Banned(PageBase):