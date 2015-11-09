import random

name="Dibbler"
description = "For displaying your credit on Dibbler"

class Page(PageBase):
	#maskv4 = (129, 241, 210)#ipv6?
	maskv4 = (127,0,0)#ipv6?
	usage="""<h1>Dibbler</h1>

<!--MESSAGE-->
<form enctype="multipart/form-data" action="/dibbler" method="POST"><p>
	<input name="form" type="hidden" value="<!--FORM-ID-->"/>
	<input name="action" type="hidden" value="credit" />
	<input name="type" type="hidden" value="browser" />
	
	Please enter the username you want to view the credit of:<br/>
	<center>
		<input name="user" type="text" value="Enter losername here" style="font-size: 150%; margin:0px 10px; margin-bottom:20px; width:40%;" maxlength="30"/><br/>
		<input type="submit" value="Check" class="button" style="font-size: 150%;"/>
	</center>
	<!--todo: captcha?-->
</p></form>
"""
	def GetUser(self, name):#too blocking?
		# Start an SQL session
		session=Session()
		# Let's find all users with a negative credit
		users = session.query(User).filter(name == User.name).all()
		users = [(i.name, i.credit) for i in users]
		session.close()
		if len(users) <> 1:
			return False, False
		else:
			return users[0]
	def MakePage(self, request, message=None):
		form = str(random.randrange(500, 500000))
		Session = request.getSession()
		if hasattr(Session, "u_forms_dib"):#cross-site request forgery protection. not neccesary at all, but fun
			Session.u_forms_dib.append(form)
		else:
			Session.u_forms_dib = [form]
		
		p = self.usage.replace("<!--DOMAIN-->", self.Template.domain).replace("<!--FORM-ID-->", form)
		return self.Template.MakePage(request, p.replace("<!--MESSAGE-->", ("<p>%s</p>" % message) if message else ""))
	def render(self, request):
		if "action" in request.args and request.args["action"][0] == "credit":
			if "type" in request.args:
				json = request.args["type"][0] == "json"
			
			if not json:
				Session = request.getSession()
				if "form" not in request.args or not hasattr(Session, "u_forms_dib") or request.args["form"][0] not in Session.u_forms_dib:
					return self.MakePage(request, "Form not served during this session, please try again.")
			if "user" in request.args:
				name = request.args["user"][0]
				for i in name:
					if ord(i.lower()) not in (range(ord("a"), ord("z")+1)+range(ord("0"), ord("9")+1)):
						return self.MakePage(request, "Username \"%s\" not valid" % str(name))
				
				username, usercredit = self.GetUser(name)
				if not username:
					return self.MakePage(request, "Username \"%s\" not found" % str(name))
				
				if json:
					return str({"username":str(username), "credit":usercredit})
				else:
					return self.MakePage(request, str("%s's credit: %skr" % (username, usercredit)))
			
		#else:
		return self.MakePage(request)
		#print GetUser("pederbs")


#DATABASE (from dibbler project):

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, DateTime, Boolean, or_
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

db_url = "postgresql://%s:%s@%s/%s" % (Settings.conf.get("dibbler", "user"), Settings.conf.get("dibbler", "pwd"), Settings.conf.get("dibbler", "host"), Settings.conf.get("dibbler", "db"))

#engine = create_engine(conf.db_url)
engine = create_engine(db_url)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    name = Column(String(10), primary_key=True)
    card = Column(String(10))
    rfid = Column(String(10))
    credit = Column(Integer)

    name_re = r"[a-z]+"
    card_re = r"(([Nn][Tt][Nn][Uu])?[0-9]+)?"
    rfid_re = r"[0-9]*"

    def __init__(self, name, card, rfid, credit=0):
        self.name = name
        if card == '':
            card = None
        self.card = card
        if rfid == '':
            rfid = None
        self.rfid = rfid
        self.credit = credit

    def __repr__(self):
        return "<User('%s')>" % self.name

    def __str__(self):
        return self.name

    def is_anonymous(self):
        return self.card == '11122233'

class Product(Base):
    __tablename__ = 'products'

    bar_code = Column(String(13), primary_key=True)
    name = Column(String(45))
    price = Column(Integer)
    stock = Column(Integer)

    bar_code_re = r"[0-9]+"
    name_re = r".+"
    name_length = 45

    def __init__(self, bar_code, name, price, stock=0):
        self.name = name
        self.bar_code = bar_code
        self.price = price
        self.stock = stock

    def __repr__(self):
        return "<Product('%s', '%s', '%s', '%s')>" % (self.name, self.bar_code, self.price, self.stock)

    def __str__(self):
        return self.name

class PurchaseEntry(Base):
    __tablename__ = 'purchase_entries'
    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer,ForeignKey("purchases.id"))
    product_bar_code = Column(String(13),ForeignKey("products.bar_code"))
    amount = Column(Integer)

    product = relationship(Product,backref="purchases")

    def __init__(self, purchase, product, amount):
        self.product = product
        self.product_bar_code = product.bar_code
        self.purchase = purchase
        self.amount = amount
    def __repr__(self):
        return "<PurchaseEntry('%s', '%s')>" % (self.product.name, self.amount )

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    user_name = Column(String(10), ForeignKey('users.name'))
    amount = Column(Integer)
    description = Column(String(50))
    purchase_id = Column(Integer, ForeignKey('purchases.id'))

    user = relationship(User, backref=backref('transactions', order_by=time))

    def __init__(self, user, amount=0, description=None, purchase=None, penalty_ratio=1):
        self.user = user
        self.amount = amount
        self.description = description
        self.purchase = purchase
        self.penalty_ratio = penalty_ratio

    def perform_transaction(self):
        self.time = datetime.datetime.now()
        self.user.credit -= self.amount * self.penalty_ratio
        if self.purchase:
            for entry in self.purchase.entries:
                entry.product.stock -= entry.amount

class Purchase(Base):
    __tablename__ = 'purchases'

    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    #	user_name = Column(Integer, ForeignKey('users.name'))
    price = Column(Integer)
    #	performed = Column(Boolean)

    #	user = relationship(User, backref=backref('purchases', order_by=id))
    #	users = relationship(User, secondary=purchase_user, backref='purhcases'
    transactions = relationship(Transaction, order_by=Transaction.user_name, backref='purchase')
    entries = relationship(PurchaseEntry, backref=backref("purchase"))

    def __init__(self):
        pass

    def __repr__(self):
        return "<Purchase(%d, %d, '%s')>" % (self.id, self.price, self.time.strftime('%c'))

    def is_complete(self):
        return len(self.transactions) > 0 and len(self.entries) > 0

    def price_per_transaction(self):
        return self.price/len(self.transactions)

    def set_price(self):
        self.price = 0
        for entry in self.entries:
            self.price += entry.amount*entry.product.price
        if len(self.transactions) > 0:
            for t in self.transactions:
                t.amount = self.price_per_transaction()

    def perform_purchase(self):
        self.time = datetime.datetime.now()
        self.set_price()
        for t in self.transactions:
            t.perform_transaction()
#		self.user.credit -= self.price
#		self.performed = True