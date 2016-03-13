import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import json
from google.appengine.ext import ndb
from google.appengine.api import images
import db_defs
import requests
#from models import UserPicfayAsset


#Source code for this file was inspired by Wolford CS 496 lectures

#code for uploading blobs sourced from:
#thedeveloperworldisyours.com/python/gae-reading-big-csv-blobstore-python
class uploadUrl(webapp2.RequestHandler):
    #requests an upload url
    def get(self):
        url = blobstore.create_upload_url('/destination')
        results = {'url': url}
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(results))
        return

class urlDestination(blobstore_handlers.BlobstoreUploadHandler):
    #assign blobkey to photo instance
    def post(self):
        upload = self.get_uploads()[0]
        newPhoto = db_defs.Photos(photo=upload.key())
        newPhoto.put()
        results = {'key': newPhoto.key.id()}
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(results))
        return

class ViewPhoto(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, **kwargs):
        if 'pid' in kwargs:
            photo = ndb.Key(db_defs.Photos, int(kwargs['pid'])).get()
            if not photo:
                self.response.set_status(404)
                self.response.write('Photo not found\n')
                return
        if not blobstore.get(photo.photo):
            self.response.set_status(404)
            self.response.write('Photo not found\n')
        else:
            img = images.get_serving_url(photo.photo)
            results = {'url': img}
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(results))
            return

class Photos(webapp2.RequestHandler):
    def get(self, **kwargs):
        #check to see if the request is in appropriate format
        if 'application/json' not in self.request.accept:
            self.response.set_status(406)
            self.response.write('API only supports JSON requests\n')
            return

        #look for id in the args, if there, return info for just that id
        if 'pid' in kwargs:
            photo = ndb.Key(db_defs.Photos, int(kwargs['pid'])).get()
            if not photo:
                self.response.set_status(404)
                self.response.write('Photo not found\n')
                return
            self.response.write(json.dumps(photo.to_dict()))
            return
        #if no specified id, return all photos
        else:
            q = db_defs.Photos.query()
            photos = q.fetch()

        out=[]
        
        for p in photos:
            photoDict = p.to_dict()
            #request url for photo
            url = images.get_serving_url(p.photo)
            #add key for photo url
            photoDict['url'] = url
            out.append(photoDict)


        self.response.headers['Content=Type'] = 'application/json'
        self.response.write(json.dumps(out))
    
    #updates a photo's description
    def put(self, **kwargs):
        if 'application/json' not in self.request.accept:
            self.response.set_status(406)
            self.response.write('API only supports JSON requests\n')
            return
        
        #Check that photo exists
        if 'pid' in kwargs:
            photo = ndb.Key(db_defs.Photos, int(kwargs['pid'])).get()
            if not photo:
                self.response.set_status(404)
                self.response.write('Photo not found\n')
                return
         
        #retrieve data
        description = self.request.get('description', default_value = None)
        
        #updates values if present
        if description: 
            photo.description = description
            
        photo.put()
        out = photo.to_dict()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(out))
        
        return
        
    #deletes a specific photo
    def delete(self, **kwargs):
        #Check that photo exists
        if 'pid' in kwargs:
            photo = ndb.Key(db_defs.Photos, int(kwargs['pid'])).get()
            if not photo:
                self.response.set_status(404)
                self.response.write('Photo not found\n')
                return

            #removes all references to photo from any Day object
            q = db_defs.Day.query().fetch()
            
            for d in db_defs.Day.query().fetch():
                for p in d.photos:
                    if photo.key == p:
                        d.photos.remove(p)
                        d.put()

            #delete blobstore blob            
            blobstore.delete(photo.photo)
            #delete comments associated with photo
            ndb.delete_multi(ndb.Query(ancestor=photo.key).iter(keys_only=True))
            #delete photo
            photo.key.delete()
            
            #gather photos to show deletion
            q = db_defs.Photos.query()
            keys = q.fetch(keys_only=True)
            results = {'keys': [x.id() for x in keys]}
            self.response.headers['Content=Type'] = 'application/json'
            self.response.write(json.dumps(results))
            
        return


class Day(webapp2.RequestHandler):
    #retrieves photos for a specific day
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
        
        out=[]
        
        for p in day.photos:
            photo = p.get()
            #get dictionary of photo attributes
            photoDict = photo.to_dict()
            #request url for photo
            url = images.get_serving_url(photo.photo)
            #add key for photo url
            photoDict['url'] = url
            out.append(photoDict)


        self.response.headers['Content=Type'] = 'application/json'
        self.response.write(json.dumps(out))
  
    #adds a specific photo to specific user->trip->day
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
        
        #Check that day exists
        if 'did' in kwargs:
            day = ndb.Key(db_defs.Day, int(kwargs['did']), parent=trip.key).get()
            if not day:
                self.response.set_status(404)
                self.response.write('Day not found\n')
                return
        
        #Check that photo exists
        if 'pid' in kwargs:
            photo = ndb.Key(db_defs.Photos, int(kwargs['pid'])).get()
            if not photo:
                self.response.set_status(404)
                self.response.write('Photo not found\n')
                return
        else:
            self.response.set_status(400)
            self.response.write('Resource not found\n')
            return
        
        #retrieve data
        description = self.request.get('description', default_value = None)
        #set photo values
        if description:
            photo.description = description

        day.photos.append(photo.key)
        
        photo.put()
        day.put()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(day.to_dict()))
        return

