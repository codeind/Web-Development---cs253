import re
from handlers.Main import Main
from db.post import Post
import time
TITLE_RE = re.compile(r'^[a-zA-Z0-9_-]{1,20}$')

def page_title_str(page_title):
	return str(page_title.replace('/',''))

def valid_post(title):
	return title and Post.by_title(title) is not None

def valid_title(title):
	return title and TITLE_RE.match(title)		

class Edit(Main):
	def get(self, page_title):
		title = page_title_str(page_title)

		if self.user and valid_post(title):
			self.render("editpage.html",content=Post.by_title(title).content)

		elif self.user and valid_title(title):
			 self.render("editpage.html")

		else:
			self.redirect("/")

	def post(self, page_title):
		title = page_title_str(page_title)

		if self.user and valid_post(title):
			post = Post.by_title(title)
			post.content = self.request.get("content")
			post.put()
			# time.sleep(5)
			self.redirect('/%s' % title)

		elif self.user:
			content = self.request.get("content")
			Post.submit(title, content)
			# time.sleep(5)
			self.redirect('/%s' % title)
		
		else:
			self.redirect('/')					  		