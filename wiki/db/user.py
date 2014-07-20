from util import make_salt, salt_password, verify_pw

from google.appengine.ext import db

class User(db.Model):
	username = db.StringProperty(required = True)
	pw_hash = db.StringProperty(required = True)
	email = db.StringProperty()

	@classmethod
	def by_id(cls, uid):
		return cls.get_by_id(uid, parent = users_key())

	@classmethod
	def by_name(cls, name):
		return cls.all().filter('username =', name).get()

	@classmethod
	def register(cls, name, password, email = None):
		salted_pass = salt_password(name, password)
		user = cls(parent = users_key(),
				   username = name, 
				   pw_hash = salted_pass, 
				   email = email)
		return user

	@classmethod
	def login(cls, name, pw):
		user = cls.by_name(name)
		if user and verify_pw(name, pw, user.pw_hash):
			return user

def users_key(group = 'default'):
		return db.Key.from_path('users', group)