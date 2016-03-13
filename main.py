#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import webapp2
import json

app = webapp2.WSGIApplication([
], debug=True)

#USERS
#get all users, search by name, username, or email, or add new user
app.router.add(webapp2.Route(r'/users', 'users.User'))
#get, update, or delete user by id
app.router.add(webapp2.Route(r'/users/<id:[0-9]+><:/?>', 'users.User'))

#TRIPS
#get trips for all users
app.router.add(webapp2.Route(r'/trips', 'trips.User'))
#get all trips for a user or add trips to a user
app.router.add(webapp2.Route(r'/users/<id:[0-9]+>/trips<:/?>', 'trips.User'))
#get, update, or delete a specific trip
app.router.add(webapp2.Route(r'/users/<uid:[0-9]+>/trips/<tid:[0-9]+><:/?>', 'trips.Trip'))

#Day
#get all days for a trip or add days to a trip
app.router.add(webapp2.Route(r'/users/<uid:[0-9]+>/trips/<tid:[0-9]+>/days<:/?>', 'days.Trip'))
#get, update, or delete a specific day 
app.router.add(webapp2.Route(r'/users/<uid:[0-9]+>/trips/<tid:[0-9]+>/days/<did:[0-9]+><:/?>', 'days.Days'))

#Photos
#upload a new photo - get upload url, create new photo, add photo to a day
app.router.add(webapp2.Route(r'/get_upload_url', 'photos.uploadUrl'))
app.router.add(webapp2.Route(r'/destination', 'photos.urlDestination'))
app.router.add(webapp2.Route(r'/viewPhoto/<pid:[0-9]+><:/?>', 'photos.ViewPhoto'))
app.router.add(webapp2.Route(r'/users/<uid:[0-9]+>/trips/<tid:[0-9]+>/days/<did:[0-9]+>/photos/<pid:[0-9]+><:/?>', 'photos.Day'))
#get all photos for a specific day
app.router.add(webapp2.Route(r'/users/<uid:[0-9]+>/trips/<tid:[0-9]+>/days/<did:[0-9]+>/photos<:/?>', 'photos.Day'))
#get all photos
app.router.add(webapp2.Route(r'/photos', 'photos.Photos'))
#get a specific photo, or delete a specific photo, or update a photo's description
app.router.add(webapp2.Route(r'/photos/<pid:[0-9]+><:/?>', 'photos.Photos'))

#Comments
#add a new comment for a photo, get all comments for a photo
app.router.add(webapp2.Route(r'/photos/<pid:[0-9]+>/comments<:/?>', 'comments.Photos'))
#get, update, delete a specific comment for a specific photo
app.router.add(webapp2.Route(r'/photos/<pid:[0-9]+>/comments/<cid:[0-9]+><:/?>', 'comments.Comments'))
