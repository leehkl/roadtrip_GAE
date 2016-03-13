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

class Trip(webapp2.RequestHandler):
    #retrieves days for a trip
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
        
            days = db_defs.Day.query(ancestor = trip.key).fetch()
            out=[]
            for d in days:
                out.append(d.to_dict())
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(out))
            return
    
  #adds a day to a specific user
    def post(self, **kwargs):
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
        
        #create new day - assign trip as parent
        newDay = db_defs.Day(parent=trip.key)

        #retrieve data
        name = self.request.get('name', default_value = None)
        source = self.request.get('source', default_value = None)
        destination = self.request.get('destination', default_value = None)
        miles = self.request.get('miles', default_value = None)
        time = self.request.get('time', default_value = None)
        photos = [] 

        #set day values
        if name:
            newDay.name = name
        else:
            self.response.set_status(400)
            self.response.write("Invalid Request: Name is a required field\n")
            return
        if source:
            newDay.source = source
        if destination:
            newDay.destination = destination
        if miles:
            if is_number(miles):
                newDay.miles = float(miles)
            else:
                self.response.set_status(400)
                self.response.write('Miles is not in valid number format\n')
                return
        if time:
            if is_number(time):
                newDay.time = float(time)
            else:    
                self.response.set_status(400)
                self.response.write('Time is not in valid number format\n')
                return
        newDay.put()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(newDay.to_dict()))
        return

class Days(webapp2.RequestHandler):

    #get a specific day from a trip
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
        
        #Check that day exists
        if 'did' in kwargs:
            day = ndb.Key(db_defs.Day, int(kwargs['did']), parent=trip.key).get()
            if not day:
                self.response.set_status(404)
                self.response.write('Day not found\n')
                return
        
        out = day.to_dict()    
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(out))
        return
    
    #updates a specific day 
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
        
        #Check that day exists
        if 'did' in kwargs:
            day = ndb.Key(db_defs.Day, int(kwargs['did']), parent=trip.key).get()
            if not day:
                self.response.set_status(404)
                self.response.write('Day not found\n')
                return
        
        #retrieve data
        name = self.request.get('name', default_value = None)
        source = self.request.get('source', default_value = None)
        destination = self.request.get('destination', default_value = None)
        miles = self.request.get('miles', default_value = None)
        time = self.request.get('time', default_value = None)

        #updates values if present
        if name:
            day.name = name
        if source:
            day.source = source
        if destination:
            day.destination = destination
        if miles:
            if is_number(miles):
                day.miles = float(miles)
            else:
                self.response.set_status(400)
                self.response.write('Miles is not in valid number format\n')
                return
        if time:
            if is_number(time):
                day.time = float(time)
            else:    
                self.response.set_status(400)
                self.response.write('Time is not in valid number format\n')
                return
        day.put()
        out = day.to_dict()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(out))
        return
    
    #deletes a specific day 
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
        
        #Check that day exists
        if 'did' in kwargs:
            day = ndb.Key(db_defs.Day, int(kwargs['did']), parent=trip.key).get()
            if not day:
                self.response.set_status(404)
                self.response.write('Day not found\n')
                return

        #delete photo
        for p in day.photos:
            photoObj = ndb.Key(db_defs.Photos, p.id()).get()
            blobstore.delete(photoObj.photo)
            #delete comments associated with photo
            ndb.delete_multi(ndb.Query(ancestor=p).iter(keys_only=True))
            p.delete()

        #delete trip
        day.key.delete()
        
        #gather days to show deletion
        q = db_defs.Day.query()
        keys = q.fetch(keys_only=True)
        results = {'keys': [x.id() for x in keys]}
        self.response.headers['Content=Type'] = 'application/json'
        self.response.write(json.dumps(results))

        return
