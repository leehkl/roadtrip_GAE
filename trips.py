import webapp2
import json
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
import db_defs


#Source code for this file was inspired by Wolford CS 496 lectures

#the following code inspired by: 
#stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float-in-python
def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


class User(webapp2.RequestHandler):
    #retrieves trips
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
            trips = db_defs.Trip.query(ancestor = user.key).fetch()
#            trips = {'keys': [x.id() for x in keys]}
            out=[]
            for t in trips:
                out.append(t.to_dict())

            self.response.headers['Content=Type'] = 'application/json'
            self.response.write(json.dumps(out))
            return
        #if no specified id, check for search parameters
        else:
            q = db_defs.Trip.query()
            if self.request.get('name', None):
                q = q.filter(db_defs.Trip.name == self.request.get('name'))
            if self.request.get('source', None):
                q = q.filter(db_defs.Trip.source == self.request.get('source'))
            if self.request.get('destination', None):
                q = q.filter(db_defs.Trip.destination == self.request.get('destination'))
            if self.request.get('mode', None):
                q = q.filter(db_defs.Trip.mode == self.request.get('mode'))
            trips = q.fetch()
            out=[]
            for t in trips:
                out.append(t.to_dict())

            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(out))

    
  #adds a trip to a specific user
    def post(self, **kwargs):
        #check to see if the request is in appropriate format
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
        
        #create new trip - assign user as parent
        newTrip = db_defs.Trip(parent=user.key)

        #retrieve data
        name = self.request.get('name', default_value = None)
        source = self.request.get('source', default_value = None)
        destination = self.request.get('destination', default_value = None)
        miles = self.request.get('miles', default_value = None)
        time = self.request.get('time', default_value = None)
        mode = self.request.get('mode', default_value = None)
        
        #set trip values
        if name:
            newTrip.name = name
        else:
            self.response.set_status(400)
            self.response.write("Invalid Request: Name is a required field\n")
            return
        if source:
            newTrip.source = source
        if destination:
            newTrip.destination = destination
        if miles:
            if is_number(miles):
                newTrip.miles = float(miles)
            else:
                self.response.set_status(400)
                self.response.write('Miles is not in valid number format\n')
                return
        if time:
            if is_number(time):
                newTrip.time = float(time)
            else:    
                self.response.set_status(400)
                self.response.write('Time is not in valid number format\n')
                return
        if mode:
            newTrip.mode = mode
        newTrip.user = user.key
        newTrip.put()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(newTrip.to_dict()))
        return

class Trip(webapp2.RequestHandler):
    
    #retrieves specific trip
    def get(self, **kwargs):
        #check to see if the request is in appropriate format
        if 'application/json' not in self.request.accept:
            self.response.set_status(406)
            self.response.write('API only supports JSON requests\n')
            return
        
        #Check that user exists
        if 'uid' in kwargs:
            user = ndb.Key(db_defs.Users, int(kwargs['uid'])).get()
            if not user:
                self.response.set_status(404)
                self.response.write('User not found\n')
                return

        #Check that trip exists
        if 'tid' in kwargs:
            trip = ndb.Key(db_defs.Trip, int(kwargs['tid']), parent=user.key).get()
            if not trip:
                self.response.set_status(404)
                self.response.write('Trip not found\n')
                return
        
        out = trip.to_dict()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(out))
        return
    
    #updates a user's trip 
    def put(self, **kwargs):
        if 'application/json' not in self.request.accept:
            self.response.set_status(406)
            self.response.write('API only supports JSON requests\n')
            return
        
        #Check that user exists
        if 'uid' in kwargs:
            user = ndb.Key(db_defs.Users, int(kwargs['uid'])).get()
            if not user:
                self.response.set_status(404)
                self.response.write('User not found\n')
                return

        #Check that trip exists
        if 'tid' in kwargs:
            trip = ndb.Key(db_defs.Trip, int(kwargs['tid']), parent=user.key).get()
            if not trip:
                self.response.set_status(404)
                self.response.write('Trip not found\n')
                return
        
        #retrieve data
        name = self.request.get('name', default_value = None)
        source = self.request.get('source', default_value = None)
        destination = self.request.get('destination', default_value = None)
        miles = self.request.get('miles', default_value = None)
        time = self.request.get('time', default_value = None)
        mode = self.request.get('mode', default_value = None)

        #updates values if present
        if name:
            trip.name = name
        if source:
            trip.source = source
        if destination:
            trip.destination = destination
        if miles:
            if is_number(miles):
                trip.miles = float(miles)
            else:
                self.response.set_status(400)
                self.response.write('Miles is not in valid number format\n')
                return
        if time: 
            if is_number(time):
                trip.time = float(time)
            else:    
                self.response.set_status(400)
                self.response.write('Time is not in valid number format\n')
                return
        if mode: 
            trip.mode = mode
        trip.put()
        out = trip.to_dict()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(out))
        return
    
    #deletes a specific trip
    def delete(self, **kwargs):
        #Check that user exists
        if 'uid' in kwargs:
            user = ndb.Key(db_defs.Users, int(kwargs['uid'])).get()
            if not user:
                self.response.set_status(404)
                self.response.write('User not found\n')
                return

        #Check that trip exists
        if 'tid' in kwargs:
            trip = ndb.Key(db_defs.Trip, int(kwargs['tid']), parent=user.key).get()
            if not trip:
                self.response.set_status(404)
                self.response.write('Trip not found\n')
                return

        #delete trip and all associated children
        #code inspired by: stackoverflow.com/questions/16576700/hot-to-delete-an-entity-including-all-children

        #delete all photos associated with trip
        days = db_defs.Day.query(ancestor=trip.key).fetch()
        for d in days:
            for p in d.photos:
                photoObj = ndb.Key(db_defs.Photos, p.id()).get()
                #self.response.write(photoObj.photo)
                blobstore.delete(photoObj.photo)
                ndb.delete_multi(ndb.Query(ancestor=p).iter(keys_only=True))
                p.delete()

            
        #delete trip and all children
        ndb.delete_multi(ndb.Query(ancestor=trip.key).iter(keys_only = True))
        #delete trip
        trip.key.delete()
        
        #gather trips to show deletion
        q = db_defs.Trip.query()
        keys = q.fetch(keys_only=True)
        results = {'keys': [x.id() for x in keys]}
        self.response.headers['Content=Type'] = 'application/json'
        self.response.write(json.dumps(results))
        
        return
