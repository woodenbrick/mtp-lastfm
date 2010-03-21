#!/usr/bin/env python

from google.appengine.ext import webapp
register = webapp.template.create_template_register()

def truncate(value, max):
    if len(value) < max:
        return value
    else:
        return value[:max] + "..."

register.filter(truncate)

def datetime_from_string(value):
    from datetime import datetime
    return datetime.strptime(value[0:-6], "%Y-%m-%dT%H:%M:%S")
    
register.filter(datetime_from_string)

def percentage(value, max):
    str = "%s%%" % (int (value / float(max) * 100))
    return str
    
register.filter(percentage)