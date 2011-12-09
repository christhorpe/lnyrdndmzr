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

import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch

import helpers


class MainHandler(webapp.RequestHandler):
    def get(self):
		people = []
		lanyrd = self.request.get("lanyrd")
		number = self.request.get("number")
		if number:
			try:
				number = int(number)
			except:
				number = 5
		else:
			number = 5
		yqlquery = "select href from html where url=\""+ lanyrd +"\" and xpath=\"//div[@class='trackers-placeholder placeholder']/ul/li/a\""
		logging.warn(yqlquery)
		results = helpers.do_yql(yqlquery)["query"]["results"]["a"]
		maxrandoms = (len(results) - 1) * number
		maxvalue = len(results) - 1
		randomquery = "http://www.random.org/integers/?num=" + str(maxrandoms) + "&min=0&max="+ str(maxvalue) +"&col=1&base=10&format=plain&rnd=new"
		result = urlfetch.fetch(randomquery)
		if result.status_code == 200:
			randoms = result.content.split("\n")
			self.response.out.write("Array of "+ str(maxrandoms) +" random numbers from Random.org<br /><br />" + str(randoms) + "<br /><br />Selection of "+ str(number)+ " random trackers from "+ str(len(results)) + " of " + lanyrd +":<br /><br />")
			for i in randoms:
				if len(people) < number:
					try:
						name = results[int(i)]["href"].replace("/profile/", "").replace("/", "")
						if name not in people:
							people.append(name)
							self.response.out.write(name + "<br />")
					except:
						self.response.out.write("<br />")
				else:
					break

def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
