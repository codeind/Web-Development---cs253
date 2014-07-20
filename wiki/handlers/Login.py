from handlers.Main import Main
from db.user import User


class Login(Main):
	def get(self):
		self.render("login.html")

	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")

		check_user = User.login(username,password)

		if check_user :
			self.login(check_user)
			self.redirect("/")

		else:
			error = "Invalid Login Details"
			self.render("login.html",error_username=error)					