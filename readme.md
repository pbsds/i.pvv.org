# [i.pvv.org](http://i.pvv.org/)


A simple, minimalistic and expandable webserver providing simple web services.

The server built with Twisted and loads all .py files in /services as their own page.
The service must set these names:
* `name`: A string displayed on the frontpage in bold.
* `description`: The description displayed on the frontpage
* `show`: boolean value on wether the service should be shown on the frontpage or not
* `Page`: A Twisted Resource class, your service's top node. 

These are added to `__builtin__` for the services to use:
* `PageBase` - A modified Twisted Resource class, which handles 404 replies and provides the object Template in self. Template mainly contains the function MakePage(request, body, title=None), used to dress up the output html body nicely.
* `Services` - A dictionary containing all the services as modules, indexed by name
* `Settings` - Contains the config in a ConfigParser object under the name "conf"
* `reactor` - in case you need access to it before reactor.run() is called

Dependencies:
* [Twisted](https://twistedmatrix.com/)
* [pyOpenSSL](https://pypi.python.org/pypi/pyOpenSSL)
* And because of OpenSSL: [service_identity](https://pypi.python.org/pypi/service_identity)
* [SQLAlchemy](http://www.sqlalchemy.org/)
