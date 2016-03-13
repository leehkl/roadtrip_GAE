import webapp2
import json
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
import db_defs
import re

#Source code for this file was inspired by Wolford CS 496 lectures

#actions on a user
class User(webapp2.RequestHandler):
    #retrieves users
    def get(self, **kwargs):
        #check to see if the request is in appropriate format
        if 'application/json' not in self.request.accept:
            self.response.set_status(406)
            self.response.write('API only supports JSON requests\n')
            return

        #look for id in the args, if there, return info for just that id
        if 'id' in kwargs:
            user = ndb.Key(db_defs.Users, int(kwargs['id'])).get()
            if not user:
                self.response.set_status(404)
                self.response.write('User not found\n')
                return
            self.response.write(json.dumps(user.to_dict()))
        #if no specified id, check for search parameters
        else:
            q = db_defs.Users.query()
            if self.request.get('name', None):
                q = q.filter(db_defs.Users.name == self.request.get('name'))
            if self.request.get('username', None):
                q = q.filter(db_defs.Users.username == self.request.get('username'))
            if self.request.get('email', None):
                q = q.filter(db_defs.Users.email == self.request.get('email'))
            keys = q.fetch(keys_only=True)
#            results = []
            results = {'keys': [x.id() for x in keys]}
#            for x in keys:
#                results.append({'key': x.id()})
#            response = {}
#            response['Users'] = results
            self.response.headers['Content=Type'] = 'application/json'
            self.response.write(json.dumps(results))

    #creates a NEW user
    def post(self):
        #check to see if the request is in appropriate format
        if 'application/json' not in self.request.accept:
            self.response.set_status(406)
            self.response.write('API only supports JSON requests\n')
            return

        #assigns user input
        newUser = db_defs.Users()
        username = self.request.get('username', default_value = None)
        password = self.request.get('password', default_value = None)
        name = self.request.get('name', default_value = None)
        city = self.request.get('city', default_value = None)
        email = self.request.get('email', default_value = None)

        #checks for required fields
        if username:
            newUser.username = username
        else:
            self.response.set_status(400)
            self.response.write("Invalid Request: Username is a required field\n")
            return
        if password:
            newUser.password = password
        else:
            self.response.set_status(400)
            self.response.write("Invalid Request: Password is a required field\n")
            return
        if name:
            newUser.name = name
        else:
            self.response.set_status(400)
            self.response.write("Invalid Request: Name is a required field.\n")
            return
        if email and re.match(r"([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)", email):
            newUser.email = email
        else:
            self.response.set_status(400)
            self.response.write("Invalid Request: Email is invalid/required field\n")
            return
        #assign remaining fields
        if city: 
            newUser.city = city
        key = newUser.put()
        out = newUser.to_dict()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(out))
        return
    
    #updates a user's profile
    def put(self, **kwargs):
        if 'application/json' not in self.request.accept:
            self.response.set_status(406)
            self.response.write('API only supports JSON requests\n')
            return

        #Check that user exists
        if 'id' in kwargs:
            user = ndb.Key(db_defs.Users, int(kwargs['id'])).get()
            if not user:
                self.response.set_status(404)
                self.response.write('User not found\n')
                return
        else:
            self.response.set_status(400)
            self.response.write('Resource not found\n')
            return
        
        #retrieve data
        username = self.request.get('username', default_value = None)
        password = self.request.get('password', default_value = None)
        name = self.request.get('name', default_value = None)
        city = self.request.get('city', default_value = None)
        email = self.request.get('email', default_value = None)

        #updates values if present
        if username:
            user.username = username
        if password:
            user.password = password
        if name:
            user.name = name
        if email: 
            if re.match(r"([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)", email):
                user.email= email
            else:
                self.response.set_status(400)
                self.response.write("Invalid Request: Email is invalid/required field\n")
                return
        if city: 
            user.city = city
        user.put()
        out = user.to_dict()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(out))
        return
    
    #Deletes a user
    def delete(self, **kwargs):
        if 'application/json' not in self.request.accept:
            self.response.set_status(406)
            self.response.write('API only supports JSON requests\n')
            return
        
        #Check that user exists
        if 'id' in kwargs:
            user = ndb.Key(db_defs.Users, int(kwargs['id'])).get()
            if not user:
                self.response.set_status(404)
                self.response.write('User not found\n')
                return
        
        #delete user and all associated children
        #code inspired by: stackoverflow.com/questions/16576700/hot-to-delete-an-entity-including-all-children

        #delete all photos associated with user
        days = db_defs.Day.query(ancestor=user.key).fetch()
        for d in days:
            for p in d.photos:
                photoObj = ndb.Key(db_defs.Photos, p.id()).get()
                #self.response.write(photoObj.photo)
                blobstore.delete(photoObj.photo)
                ndb.delete_multi(ndb.Query(ancestor=p).iter(keys_only=True))
                p.delete()

        #delete all comments made by the user
        comments = db_defs.Comments.query().fetch()
        for c in comments:
            if c.username == user.key:
                c.key.delete()
            
        #delete user and all children
        ndb.delete_multi(ndb.Query(ancestor=user.key).iter(keys_only = True))
        user.key.delete()
        
        #gather users to show deletion
        q = db_defs.Users.query()
        keys = q.fetch(keys_only=True)
        results = {'keys': [x.id() for x in keys]}
        self.response.headers['Content=Type'] = 'application/json'
        self.response.write(json.dumps(results))
        
        return
