#!/usr/bin/env python

from google.appengine.ext import db

class Device(db.Model):
    model = db.StringProperty()
    manufacturer = db.StringProperty()
    user_count = db.IntegerProperty(default=0)
    not_working_count = db.IntegerProperty(default=0)
    comment_count = db.IntegerProperty(default=0)

class User(db.Model):
    username = db.StringProperty()
    device_friendly_name = db.StringProperty()
    device = db.ReferenceProperty(Device)
    not_working = db.BooleanProperty()
    
class Comment(db.Model):
    user = db.ReferenceProperty(User)
    device = db.ReferenceProperty(Device, collection_name="device_collection")
    comment = db.TextProperty()
    date = db.DateTimeProperty(auto_now=True)
    