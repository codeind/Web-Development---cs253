from handlers.Main import Main



class Logout(Main):
	def get(self):
		self.logout()
		self.redirect("/")