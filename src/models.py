#!/usr/bin/env python

from google.appengine.ext import db

class Device(db.Model):
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