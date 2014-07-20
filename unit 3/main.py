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

from google.appengine.ext import db

template_dir=os.path.join(os.path.dirname(__file__), 'templates')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


def render_str(template,**params):
    t=jinja_env.get_template(template)
    return t.render(params)
   

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
                                  



app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                              ],
                              debug=True)






