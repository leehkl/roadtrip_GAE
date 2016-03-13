import webapp2
from google.appengine.ext import blobstore
import json
import base_page
from google.appengine.ext import ndb
from google.appengine.api import images
import db_defs
#from models import UserPicfayAsset


class Admin(base_page.BaseHandler):
    def __init__(self, request, response):
        self.initialize(request, response)
        self.template_values={}
        self.template_values['upload_url'] = blobstore.create_upload_url('/upload_photo')

    def render(self, page):
        #self.response.headers['Content-Type']='application/json'
        obj = {
                'uploadUrl': self.template_values['upload_url'],   
                'description': self.request.get('description') 
        }
        self.response.out.write(json.dumps(obj))

        photos = db_defs.Photos
        self.response.out.write(photos)
#        self.response.out.write(images.get_serving_url(photos.photo, crop=True, size=64))

        base_page.BaseHandler.render(self, page, self.template_values)

    
    def get(self):
        self.render('admin.html')

    def post(self, icon_key=None):
        #k=ndb.Key(db_defs.Day, self.app.config.get('default-group'))
#        day=db_defs.Day()
 #       day.put()
 #       dkey = ndb.Key(db_defs.Day, day)
        #k=ndb.Key(db_defs.Photos, self.app.config.get('default-group'))
        p1=db_defs.Photos()
        p1.photo=icon_key
        p1.description = self.request.get('description')
#        day.photos = p1.key()
#        day.photos.append(icon_key)
        p1.put()
        self.render('admin.html')
            

