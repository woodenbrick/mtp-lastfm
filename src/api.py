# Copyright 2009 Daniel Woodhouse
#
#This file is part of mtp-lastfm.
#
#mtp-lastfm is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#mtp-lastfm is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with mtp-lastfm.  If not, see http://www.gnu.org/licenses/


"""This file is not required by mtp-lastfm, it sits on a GAE server and collects
data such as usage statistics and non working devices"""

import os
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from cgi import escape

class Usage(db.Model):
    model = db.StringProperty()
    manufacturer = db.StringProperty()
    issues = db.IntegerProperty()
    count = db.IntegerProperty()

class UsersWithProblems(db.Model):
    email = db.StringProperty()
    device_friendly_name = db.StringProperty()
    
class Problems(db.Model):
    libmtp_version = db.StringProperty()
    manufacturer = db.StringProperty()
    model = db.StringProperty()
    dump = db.BlobProperty()
    user = db.ReferenceProperty(UsersWithProblems)



class UsageStatistics(webapp.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = "text/plain"
        model = escape(self.request.get("model"))
        manufacturer = escape(self.request.get("manufacturer"))
        if model == "" or manufacturer == "":
            self.response.set_status(400)
            self.response.out.write("MISSINGVALUES")
            return
        usage = Usage.all().filter("model =", model).filter("manufacturer =", manufacturer).get()
        if usage is None:
            usage = Usage(model=model, manufacturer=manufacturer, issues=0, count=1)
        else:
            usage.count += 1
        usage.put()
        self.response.out.write("OK")
            
    def get(self):
        devices = Usage.all().order("manufacturer")
        dev_dict = {}
        for dev in devices:
            try:
                dev_dict[dev.manufacturer]
            except KeyError:
                dev_dict[dev.manufacturer] = []
            dev_dict[dev.manufacturer].append(dev)
        template_path = os.path.join(os.path.dirname(__file__), "templates", "usage.html")
        self.response.headers['Content-Type'] = "text/html"
        self.response.out.write(template.render(template_path, {"devices" : dev_dict}))

        
class HasIssues(webapp.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = "text/plain"
        name = escape(self.request.get("friendly_name"))
        email = escape(self.request.get("email"))
        comment = escape(self.request.get("comment"))
        model = escape(self.request.get("model"))
        libmtp_version = escape(self.request.get("libmtp_version"))
        manufacturer = escape(self.request.get("manufacturer"))
        dump = self.request.get("dump")
        #check if this device has a reported issue already
        userprob = UsersWithProblems.all().filter("device_friendly_name =", name).filter("model =", model).get()
        if userprob is None:
            userprob = UsersWithProblems(device_friendly_name=name, email=email)
            userprob.put()
            mod = Usage.all().filter("model =", model).filter("manufacturer =", manufacturer).get()
            mod.issues += 1
            mod.put()
        problem = Problems(model=model, libmtp_version=libmtp_version, dump=dump,
                               user=userprob, comment=comment)
        problem.put()
        self.response.out.write("OK")
            
    def get(self):
        issue = Problems.all().get()
        self.response.headers['Content-Type'] = "text/plain"
        self.response.out.write(issue.dump)
        

class Error(webapp.RequestHandler):
    def get(self, page):
        self.response.headers['Content-Type'] = "text/xml"
        self.response.set_status(400, "FUCK")
        self.response.out.write(template.render("templates/lfmerror.xml", {}))


class AddNew(webapp.RequestHandler):
    #not production code
    def get(self):
        model = "Pen 2"
        manufacturer="Ham Ltd"
        x = Usage.all().filter("model =", model).filter("manufacturer =", manufacturer).get()
        if x is None:
            x = Usage(model=model, manufacturer=manufacturer, count=1)
        else:
            x.count += 1
        x.put()
        
application = webapp.WSGIApplication([
    ('/hasissue', HasIssues),
    ('/usage', UsageStatistics),
    ('/addnew', AddNew),
    (r'/(.*)', Error),
    
], debug=True)

run_wsgi_app(application)


