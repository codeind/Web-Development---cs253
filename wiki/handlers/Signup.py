from handlers.Main import Main
from util import valid_name, valid_pass, valid_email
from db.user import User




class Signup(Main):

	def get(self):
		self.render('signup.html')

	def post(self):
		has_error = False
		self.username = self.request.get("username")
		self.password = self.request.get("password")
		self.confirm = self.request.get("verify")
		self.email = self.request.get("email")

		params = dict(username = self.username, email = self.email)

		if not valid_name(self.username):
			params["error_username"]="Invalid Username"
			has_error = True

		if not valid_pass(self.password):
			params['error_password']='invalid password'
			has_error = True
		
		if self.email !="":
			if not valid_email(self.email):
				params["error_email"] = "Invalid email"
				has_error = True

		if self.password != self.confirm:
			params["error_confirm"] = "Password does not match"	
			has_error = True
			
		if has_error:
			self.render("signup.html", **params)

		else:
			u = User.by_name(self.username)

			if u:
				error = "Username already exists! Please choose another username"
				self.render("signup.html",error_username=error)

			else:
				user = User.register(self.username, self.password, self.email)
				user.put()
				self.login(user)
				self.redirect("/")	


