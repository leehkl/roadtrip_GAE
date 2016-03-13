from google.appengine.ext import ndb

class Model(ndb.Model):
    def to_dict(self):
        d = super(Model, self).to_dict()
        d['key'] = self.key.id()
        return d

class Users(Model):
    username = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    city = ndb.StringProperty(required=False)
    email = ndb.StringProperty(required=True)
    
class Trip(Model):
    name = ndb.StringProperty(required=True)
    source = ndb.StringProperty(required=False)
    destination = ndb.StringProperty(required=False)
    miles = ndb.FloatProperty(required=False)
    time = ndb.FloatProperty(required=False)
    mode = ndb.StringProperty(required=False)
    user = ndb.KeyProperty(required=True)
    
    def to_dict(self):
        d = super(Trip, self).to_dict()
        d['user'] = d['user'].id()
        return d
    

class Day(Model):
    name = ndb.StringProperty(required = True)
    source = ndb.StringProperty(required=False)
    destination = ndb.StringProperty(required=False)
    miles = ndb.FloatProperty(required=False)
    time = ndb.FloatProperty(required=False)
    photos = ndb.KeyProperty(repeated=True)

    def to_dict(self):
        d = super(Day, self).to_dict()
        d['photos'] = [p.id() for p in d['photos']]
        return d

class Photos(Model):
    photo = ndb.BlobKeyProperty(required=True)
    description = ndb.TextProperty(required=False)
    
    def to_dict(self):
        d = super(Model, self).to_dict()
        d['photo'] = self.key.id()
        return d

class Comments(Model):
    comment = ndb.TextProperty(required=True)
    username = ndb.KeyProperty(required=False)
    
    def to_dict(self):
        d = super(Model, self).to_dict()
        if d['username']:
            d['username'] = d['username'].id()
        return d
