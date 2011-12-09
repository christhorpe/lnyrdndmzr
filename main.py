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
		# gets the Lanyrd URL
		lanyrd = self.request.get("lanyrd")
		# gets the number of winners
		number = self.request.get("number")
		# casts the number to an int, defaults to 5 randoms if no number specified
		if number:
			try:
				number = int(number)
			except:
				number = 5
		else:
			number = 5
		# does the YQL thing to get the people tracking on Lanyrd
		yqlquery = "select href from html where url=\""+ lanyrd +"\" and xpath=\"//div[@class='trackers-placeholder placeholder']/ul/li/a\""
		logging.warn(yqlquery)
		# need to put some handling in here for when there are no trackers, assumes that there are
		results = helpers.do_yql(yqlquery)["query"]["results"]["a"]
		if results:
			# gets a lot more random numbers than needed, but useful where small sample sets to avoid collisions, needs optimising for when there are a big number of trackers or a large number of randoms needed, or god forbid both
			maxrandoms = (len(results) - 1) * number
			maxvalue = len(results) - 1
			# build query for Random.org
			randomquery = "http://www.random.org/integers/?num=" + str(maxrandoms) + "&min=0&max="+ str(maxvalue) +"&col=1&base=10&format=plain&rnd=new"
			# and go fetch it
			result = urlfetch.fetch(randomquery)
			if result.status_code == 200:
				# each number is on a new line, so split into an array, sadly it'll have 1 item left over, TODO fix trailing \n
				randoms = result.content.split("\n")
				# put something out on top of page to show how many numbers and for true transparency give the array of random numbers
				self.response.out.write("<div>Array of "+ str(maxrandoms) +" random numbers from Random.org</div><hr /><div>" + str(randoms) + "</div><hr /><div>Selection of "+ str(number)+ " random trackers from "+ str(len(results)) + " of " + lanyrd +":</div><br />")
				# iterate throguh random numbers
				for i in randoms:
					# iterate through the random numbers
					if len(people) < number:
						# only parse if we haven't picked the n random people
						try:
							# here as a horrible hack for the trailing \n TODO clean up
							name = results[int(i)]["href"].replace("/profile/", "").replace("/", "")
							# check to see if person has been picked, greater chance in small sample sets
							if name not in people:
								# if they're not there add them to the array and display on page
								people.append(name)
								self.response.out.write("<div>" + name + "</div>")
						except:
							i = "NaN"
					else:
						break

def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
