import webapp2
import json
from google.appengine.ext import ndb
import db_defs
#from models import UserPicfayAsset


#Source code for this file was inspired by Wolford CS 496 lectures

#the following code inspired by: 
#stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float-in-python
def is_number(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

class Comments(webapp2.RequestHandler):
    #retrieves a specific comment
    def get(self, **kwargs):
        #check to see if the request is in appropriate format
        if 'application/json' not in self.request.accept:
            self.response.set_status(406)
            self.response.write('API only supports JSON requests\n')
            return

        #Check that photo exists
        if 'pid' in kwargs:
            photo = ndb.Key(db_defs.Photos, int(kwargs['pid'])).get()
            if not photo:
                self.response.set_status(404)
                self.response.write('photo not found\n')
                return
        
        #check that the comment exists
        if 'cid' in kwargs:
            comment = ndb.Key(db_defs.Comments, int(kwargs['cid']), parent=photo.key).get()
            if not comment:
                self.response.set_status(404)
                self.response.write('Comment not found\n')
                return
        
        out = comment.to_dict()
        self.response.headers['Content=Type'] = 'application/json'
        self.response.write(json.dumps(out))
    
    #updates a comment
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
                self.response.write('photo not found\n')
                return
        
        #check that the comment exists
        if 'cid' in kwargs:
            comment = ndb.Key(db_defs.Comments, int(kwargs['cid']), parent=photo.key).get()
            if not comment:
                self.response.set_status(404)
                self.response.write('Comment not found\n')
                return
        
        #retrieve data
        commentStr = self.request.get('comment', default_value = None)

        #updates values if present
        if commentStr: 
            comment.comment = commentStr
        comment.put()
        out = comment.to_dict()
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
                self.response.write('photo not found\n')
                return
        
        #check that the comment exists
        if 'cid' in kwargs:
            comment = ndb.Key(db_defs.Comments, int(kwargs['cid']), parent=photo.key).get()
            if not comment:
                self.response.set_status(404)
                self.response.write('Comment not found\n')
                return
        
            #delete photo
            comment.key.delete()
            
            #gather photos to show deletion
            q = db_defs.Comments.query()
            keys = q.fetch(keys_only=True)
            results = {'keys': [x.id() for x in keys]}
            self.response.headers['Content=Type'] = 'application/json'
            self.response.write(json.dumps(results))
            
        return


class Photos(webapp2.RequestHandler):
    #retrieves comments for a specific photo
    def get(self, **kwargs):
        
        #check to see if the request is in appropriate format
        if 'application/json' not in self.request.accept:
            self.response.set_status(406)
            self.response.write('API only supports JSON requests\n')
            return

        #Check that photo exists
        if 'pid' in kwargs:
            photo = ndb.Key(db_defs.Photos, int(kwargs['pid'])).get()
            if not photo:
                self.response.set_status(404)
                self.response.write('photo not found\n')
                return
        keys = db_defs.Comments.query(ancestor = photo.key).fetch(keys_only=True)
        comments = {'keys': [x.id() for x in keys]}
        
        self.response.headers['Content=Type'] = 'application/json'
        self.response.write(json.dumps(comments))
  
    #adds a comment to a photo
    def post(self, **kwargs):
        #check to see if the request is in appropriate format
        if 'application/json' not in self.request.accept:
            self.response.set_status(406)
            self.response.write('API only supports JSON requests\n')
            return

        #Check that day exists
        if 'pid' in kwargs:
            photo = ndb.Key(db_defs.Photos, int(kwargs['pid'])).get()
            if not photo:
                self.response.set_status(404)
                self.response.write('Photo not found\n')
                return

        #make new comment, with photo as parent
        newComment = db_defs.Comments(parent=photo.key)

        #if userid is passed - check to make sure it's a valid user
        userID = self.request.get('user', default_value = None)
        if userID:
            if is_number(userID):
                user = ndb.Key(db_defs.Users, int(userID)).get()
                if not user:
                      self.response.set_status(404)
                      self.response.write('User not found\n')
                      return
                newComment.username = user.key
            else:
                self.response.set_status(400)
                self.response.write('UserID is not in a valid int format\n')
                return
        #retrieve data
        comment = self.request.get('comment', default_value = None)

        #set photo values
        if comment:
            newComment.comment = comment
        else:
            self.response.set_status(400)
            self.response.write("Invalid Request: Comment is a required field\n")
            return

        newComment.put()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(newComment.to_dict()))
        return

