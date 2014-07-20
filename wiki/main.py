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
import jinja2
import webapp2
from handlers.Main import Main
from db.user import User
from db.post import Post
from handlers.Wiki import Wiki
from handlers.Edit import Edit
from handlers.Login import Login
from handlers.Logout import Logout
from handlers.Signup import Signup

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'


app = webapp2.WSGIApplication([('/', Main),
								('/login', Login),
							   ('/logout', Logout),
							   ('/signup', Signup),
							   ('/_edit' +PAGE_RE, Edit),
							   (PAGE_RE, Wiki),
		
							  ],
							  debug=True)






