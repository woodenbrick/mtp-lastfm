#!/usr/bin/env python
import os
from urllib import unquote, unquote_plus
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from models import Comment, Device, User
import github
import hashlib
import templatefilters

WEB_TEMPLATE_PATH = "templates/webinterface/"
webapp.template.register_template_library('templatefilters')

class Home(webapp.RequestHandler):
    def get(self):
        gh = github.GitHub()
        data = {}
        data['github'] = gh.commits.forBranch("woodenbrick", "mtp-lastfm")[0]
        data['gravatar'] = hashlib.md5(data['github'].author.email).hexdigest()
        self.response.out.write(template.render(WEB_TEMPLATE_PATH + "home.html",
                                                data))
        
class Install(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render(WEB_TEMPLATE_PATH + "install.html", {}))

class Contact(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render(WEB_TEMPLATE_PATH + "contact.html", {}))

class Screenshot(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render(WEB_TEMPLATE_PATH + "screenshots.html", {}))

class UsageAll(webapp.RequestHandler):
    def get(self):
        devices = Device.all().order("manufacturer")
        dev_dict = {}
        for dev in devices:
            try:
                dev_dict[dev.manufacturer]
            except KeyError:
                dev_dict[dev.manufacturer] = []
            dev_dict[dev.manufacturer].append(dev)
        self.response.headers['Content-Type'] = "text/html"
        self.response.out.write(template.render(WEB_TEMPLATE_PATH + "usage.html",
                                                {"devices" : dev_dict}))


class UsageDevice(webapp.RequestHandler):
    def get(self, man, model):
        man = unquote_plus(unquote(man))
        model = unquote_plus(unquote(model))
        device = Device.all().filter("manufacturer = ", man).filter("model =", model).get()
        if device is None:
            self.response.headers['Content-Type'] = "text/html"
            self.response.out.write("No such device: %s - %s" % (man, model))
        else:
            comments = [c for c in device.device_collection]
            self.response.out.write(template.render(WEB_TEMPLATE_PATH + "device.html",
                                                    {"device" : device,
                                                     "comments" : comments}))

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
        

application = webapp.WSGIApplication([
    ('/device/all', UsageAll),
    ('/device/(.*)/(.*)', UsageDevice),
    ('/install', Install),
    ('/contact', Contact),
    ('/screenshots', Screenshot),
    ('/', Home)
], debug=True)

run_wsgi_app(application)