import os
import jinja2
import webapp2
from db.user import User
from google.appengine.ext import db
from util import make_secure_val, check_secure_val
import time
templates_dir = os.path.join(os.path.dirname(__file__),'../templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_dir), autoescape=False)


def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)


class Main(webapp2.RequestHandler):

	def write(self, *args, **kw):
		self.response.out.write(*args, **kw)

	def render_str(self,template,**kw):
		kw['user'] = self.user
		return render_str(template,**kw)

	def render(self,template,**kw):
		self.write(self.render_str(template,**kw))

	def get(self):
		self.response.write()

	def set_cookie(self,name,val):
		secure_val = make_secure_val(val)	
		self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, secure_val))

	def check_cookie(self,name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)

	def login(self, username):
		self.set_cookie('user_id', str(username.key().id()))

	def logout(self):
		self.response.headers.add_header('Set-Cookie','user_id=; Path=/')	

	def get(self):
		self.render("base.html")

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		user = self.check_cookie('user_id')
		self.user = user and User.by_id(int(user))				

