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

from models import Device

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
        handler.response.headers['Content-Type'] = "text/xml"
        handler.response.set_status(400, "NOTFOUND")
        handler.response.out.write(template.render("templates/error.xml",
                                            {"status" : error_code,
                                             "error_msg" : msg}))

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
    ('/api/devices', AllDevices),
    ('/api/devices/(.*)', DevicesByManufacturer),
    ('/api/devices/(.*)/(.*)', SingleDevice),
    ('/api/addnew', AddNew),
    (r'/api/(.*)', Error),
    
], debug=True)

run_wsgi_app(application)


