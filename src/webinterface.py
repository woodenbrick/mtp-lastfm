#!/usr/bin/env python

from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

WEB_TEMPLATE_PATH = "templates/webinterface"

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
        

application = webapp.WSGIApplication([
    ('/usage', UsageStatistics),
], debug=True)

run_wsgi_app(application)