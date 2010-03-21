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
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from cgi import escape
from models import Comment, Device, User

API_TEMPLATE_PATH = "templates/api/"


class AllDevices(webapp.RequestHandler):
    def get(self):
        devices = Device.all().fetch(1000)
        status = "OK" if len(devices) != 0 else "NOTFOUND"
        self.response.headers['Content-Type'] = "text/xml"
        self.response.out.write(template.render(API_TEMPLATE_PATH + "devices.xml",
                                                {"status" : status, "devices" : devices}))

class DevicesByManufacturer(webapp.RequestHandler):
    pass

class SingleDevice(webapp.RequestHandler):
    pass

class Error(webapp.RequestHandler):
    def get(self, page):
        self.response.headers['Content-Type'] = "text/xml"
        self.response.set_status(400, "NOTFOUND")
        self.response.out.write(template.render("templates/error.xml",
                                            {"status" : error_code,
                                             "error_msg" : msg}))

class AddNew(webapp.RequestHandler):
    def post(self):
        model = self.request.get("model")
        manufacturer = self.request.get("manufacturer")
        username = self.request.get("username")
        dev_name = self.request.get("name")
        not_working = int(self.request.get("not_working"))
        comment = escape(self.request.get("comment").strip())
        
        #get device
        device = Device.all().filter("manufacturer =", manufacturer).filter(
            "model =", model).get()
        if device is None:
            device = Device(manufacturer=manufacturer, model=model)
            device.put()
        user = User.all().filter("username =", username).filter(
            "device_friendly_name =", dev_name).filter(
    "device =", Device.gql("WHERE model=:1", model).get()).get()
        if user is None:
            user = User(username=username, device_friendly_name=dev_name,
            device=device, not_working=bool(not_working))
            user.put()
            device.user_count += 1
            device.not_working_count += not_working
            device.put()
        else:
            if user.not_working != not_working:
                #got a bit of mindchanging here cirrus...
                if not_working == 1:
                    device.not_working_count += 1
                else:
                    device.not_working_count -= 1
                device.put()
        if comment != "":
            new_comment = Comment(user=user, comment=comment, device=device)
            new_comment.put()
            device.comment_count += 1
        user.put()
        device.put()
            
        
        
application = webapp.WSGIApplication([
    ('/api/devices', AllDevices),
    ('/api/devices/(.*)', DevicesByManufacturer),
    ('/api/devices/(.*)/(.*)', SingleDevice),
    ('/api/add', AddNew),
   # (r'/api/(.*)', Error),
    
], debug=True)

run_wsgi_app(application)


