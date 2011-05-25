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
from __future__ import with_statement
import os
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from xml.dom import minidom
from google.appengine.ext import db
from mapreduce import operation as op
from mapreduce import context

class flickrTag(db.Model):
    photo_id = db.StringProperty()
    tag = db.TextProperty()
    taken = db.StringProperty()

class data(db.Model):
	data = db.TextProperty()

def fTag(id):
	url = constructUrl("flickr.photos.getInfo", {"photo_id":id})
	result = urlfetch.fetch(url)
	if result.status_code == 200:
		#self.response.headers['Content-Type'] = 'text/plain'
		dom = minidom.parseString(result.content)
		photos = dom.getElementsByTagName("photo")
		tagText = ""
		for photo in photos:
			if photo.hasAttributes():
				photo_id = photo.attributes["id"].value
				tags = dom.getElementsByTagName("tag")
				for tag in tags:
					if tag.hasAttributes():
						tagText += tag.attributes["raw"].value + ";"
		dates = dom.getElementsByTagName("dates")
		taken = ""
		for date in dates:
			if date.hasAttributes():
				taken = date.attributes["taken"].value
	return (tagText,taken)

	#member variables, 
	#please visit flickr website inorder to get an api key
m_szApiKey  = "bbdfcc265a0bb70a75163a0943b8d245"
	#nsid is the userid, please clik on the rss link on your photstream 
m_szNsid    = "user-id"	
m_szRestEnd = "http://api.flickr.com/services/rest/?"
m_pictDict = {} #Stores the urls of small and large files

	#Function creates a url based on methodname and params passed to it
def constructUrl(methodname, params={}):
	url = m_szRestEnd+"api_key="+m_szApiKey+"&method="+methodname
	if len(params) != 0:
		for key, value in params.iteritems():
			url = url+"&"+str(key)+"="+str(value)
	return url



class init(webapp.RequestHandler):
	def get(self):
		e1 = flickrTag2(photo_id="548614")
		e2 = flickrTag2(photo_id="5486140")
		e3 = flickrTag2(photo_id="54861400")
		db.put([e1,e2,e3])
	


class index(webapp.RequestHandler):
      
	def get(self):
		e = data(data="")
		db.put(e)
		self.response.out.write("Flickr Tag")
		
        



application = webapp.WSGIApplication([('/',index),('/init',init)], debug=True)

def process(entity):
	(tags,taken) = fTag(entity.photo_id)
	entity.tag = tags
	entity.taken = taken
	yield op.db.Put(entity)


def to_data(entity):
	q = data.all()
	result = q.fetch(1)
	for r in result:
		r.data += "`" + entity.photo_id+"`"+entity.tag+"`"+entity.taken
		r.put()


def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()			
			
