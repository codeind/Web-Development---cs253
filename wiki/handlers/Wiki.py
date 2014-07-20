from db.post import Post
from handlers.Main import Main

class Wiki(Main):
		def get(self, page_title):
			post = Post.by_title(str(page_title.replace('/','')))

			if post:
				self.render("wikipage.html",post=post)

			else:
				self.redirect("/_edit/%s" % str(page_title.replace('/','')))	
