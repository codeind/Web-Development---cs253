#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import re
from string import letters

import webapp2
import jinja2
import hashlib
import hmac
import random
import json
from google.appengine.ext import db

template_dir=os.path.join(os.path.dirname(__file__), 'templates')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
							   autoescape = True)


def render_str(template,**params):
	t=jinja_env.get_template(template)
	return t.render(params)
   
def make_salt(length=5):
	return ''.join(random.choice(letters) for x in range(length))

def make_pw_hash(name,pw,salt=None):
	if not salt:
	   salt = make_salt()
	h = hashlib.sha256(name+pw+salt).hexdigest()
	return '%s,%s' % (salt,hash)

def valid_pw(name,password,h):
	salt=h.split(',')[0]
	return h==make_pw_hash(name,password,salt)


secret="testsecret"


def make_secure_cookie(val):
	return "%s|%s" % (val, hmac.new(secret,val).hexdigest())	

def check_secure_val(secure_val):
	val=secure_val.split('|')[0]
	if secure_val == make_secure_cookie(val):
		return val


	

class BlogHandler(webapp2.RequestHandler):
	def write(self,*a,**kw):
		self.response.out.write(*a,**kw)

	def render_str(self,template,**params):
		return render_str(template,**params)

	def render(self,template,**params):
		self.write(self.render_str(template,**params))


def render_post(response,post):
	response.out.write('<b>' +post.title+ '</b><br>')
	response.out.write(post.content)              	

class MainPage(BlogHandler):
	def get(self):
		self.write("Hello World!")


class Post(db.Model):
	subject= db.StringProperty(required=True)
	content =db.TextProperty(required=True)
	created=db.DateTimeProperty(auto_now_add=True)
	last_modified=db.DateTimeProperty(auto_now=True)

	def render(self):
		self._render_text= self.content.replace('\n','<br>')
		return render_str('post.html',p=self)


class BlogFront(BlogHandler):
	def get(self):
		posts=db.GqlQuery("Select * from Post order by created desc limit 10")
		self.render('frontpage.html',posts=posts)


class PostPage(BlogHandler):
	def get(self,post_id):
		key=db.Key.from_path('Post',int(post_id))
		post=db.get(key)

		if not post:
		   self.error(404)
		   return
		
		self.render('permalink.html',post=post)



class NewPost(BlogHandler):
	def get(self):
		self.render("newpost.html")  

	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content") 


		if subject and content:
		   p = Post(subject=subject, content=content)
		   p.put()
		   self.redirect('/blog/%s' % str(p.key().id()))


		else:
			error = "Please enter subject and content"
			self.render("newpost.html", subject=subject,content=content,error=error) 

class User(db.Model):
	username = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	email =	db.StringProperty()						  

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")

def valid_username(username):
	return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")

def valid_password(password):
	return password and PASS_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def valid_email(email):
	return not email or EMAIL_RE.match(email)


class Signup(BlogHandler):
	def render_signup(self,name_error="", password_error="", verify_error="",email_error="",username="",email=""):
		self.render("signup-form.html", error_username=name_error,error_password=password_error,error_verify=verify_error, 
			error_email=email_error,username=username,email=email)

	def get(self):
		self.render_signup()

	def post(self):
		have_error=False
		user_name= self.request.get("username")
		user_password = self.request.get("password")
		user_verify = self.request.get("verify")
		user_email = self.request.get("email")
		name_error = password_error = verify_error = email_error=""	

		if not valid_username(user_name):
			name_error="Not valid username"
			have_error=True

		if not valid_password(user_password):
			password_error="Not valid password"
			have_error=True

		elif user_password != user_verify:
			verify_error = "password does not match"
			have_error=True

		if not valid_email(user_email):
			email_error="Not valid email"
			have_error=True

		if have_error:
			self.render_signup(name_error, password_error, verify_error, email_error, user_name, user_email)						

		else:
			u= User.gql("Where username='%s'"%user_name).get()

			if u:
				 name_error="Username already exists!"
				 self.render_signup(name_error)

			else:
				h=make_pw_hash(user_name,user_password)
				u = User(username=user_name,password=h, email=user_email)
				u.put()
				uid = str(make_secure_cookie(str(u.key().id())))
				self.response.headers.add_header('Set-Cookie','user_id=%s;Path=/' % uid)
				self.redirect('/welcome')


class Login(BlogHandler):
	def render_login_page(self,username="",error=""):
		self.render("login-form.html",username=username,error=error)

	def get(self):
		self.render_login_page()

	def post(self):
		user_name = self.request.get('username')
		user_password = self.request.get('password')
		if valid_username(user_name) and valid_password(user_password):
			cookie_str = self.request.cookies.get('user_id')

			if cookie_str:
				cookie_val = check_secure_val(str(cookie_str))
				u = User.get_by_id(int(cookie_val))
				if u and valid_pw(user_name, user_password, u.password):
					self.redirect('/welcome')

		else:
			error = 'Invalid details'
			self.render_login_page(user_name, error = error)


class Logout(BlogHandler):
	def get(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
		self.redirect('/signup')            
					



class Welcome(BlogHandler):
	 
	def get(self):
		cookie_val = self.request.cookies.get('user_id')
	 
		if cookie_val: 
			user_id = check_secure_val(str(cookie_val))	
			u = User.get_by_id(int(user_id))
			self.render('welcome.html', username = u.username)

		else:
			self.redirect('/signup')

class JsonMainHandler(BlogHandler):
	def get(self):
		self.response.headers['Content-Type']='application/json; charset=UTF-8'			
		posts = db.GqlQuery("Select * from Post Order By created desc limit 10")
		posts = list(posts)
		jsitem =[]
		for post in posts:
			d = {'content':post.content, 'subject': post.subject, 'created': post.created.strftime('%c'),
			'last_modified': post.last_modified.strftime('%c')}
			jsitem.append(d)
		self.write(json.dumps(jsitem))	

class JsonPostHandler(BlogHandler):
	def get(self, key):
		self.response.headers['Content-Type']='application/json; charset=UTF-8'		
		post = Post.get_by_id(int(key))
		d = {'content':post.content, 'subject': post.subject, 'created': post.created.strftime('%c'),
			'last_modified': post.last_modified.strftime('%c')}
		self.write(json.dumps(d))


app = webapp2.WSGIApplication([('/', MainPage),
								('/.json', JsonMainHandler),
							   ('/blog/?', BlogFront),
							   ('/blog/([0-9]+)', PostPage),
							    ('/blog/([0-9]+).json', JsonPostHandler),
							   ('/blog/newpost', NewPost),
							   ('/signup', Signup),
							   ('/login', Login),
							   ('/logout', Logout), 
							   ('/welcome', Welcome),
							  ],
							  debug=True)






