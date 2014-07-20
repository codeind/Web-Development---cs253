import re
import random
import hashlib
import hmac
from string import letters


secret = 'testsecret'
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")

def valid_name(name):
	return name and USER_RE.match(name)

PASS_RE = re.compile(r"^.{3,20}$")

def valid_pass(password):
	return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

def valid_email(email):
	return email and EMAIL_RE.match(email)

def make_salt(length = 5):
	return ''.join(random.choice(letters) for x in xrange(length))

def salt_password(name, password, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + password + salt).hexdigest()
	return '%s|%s' % (salt, h)

def verify_pw(name, password, h):
	salt = h.split('|')[0]
	return h == salt_password(name, password, salt)

def make_secure_val(val):
	return "%s|%s" % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(val):
	value = val.split('|')[0]
	if make_secure_val(value) == val:
		return value

