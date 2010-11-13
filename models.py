from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import blobstore

class Database(db.Model):
  dbid=db.StringProperty(required=True)

class Document(db.Model):
  docid=db.StringProperty(required=True)
  database=db.ReferenceProperty(Database, required=True)
  state=db.TextProperty()

class View(db.Model):
  viewid=db.StringProperty(required=True)

class Tab(db.Model):
  wave=db.ReferenceProperty(Wave, required=True)
  user=db.UserProperty(required=True)
  name=db.StringProperty(required=True)
  index=db.IntegerProperty(required=True)

class Participant(db.Model):
  wave=db.ReferenceProperty(Wave, required=True)
  user=db.UserProperty(required=True)

class Curated(db.Model):
  name=db.StringProperty(required=True)
  url=db.StringProperty(required=True)
  iconUrl=db.StringProperty(required=True)
  linkbot=db.StringProperty()

class Gadget(db.Model):
  gadgetid=db.StringProperty(required=True)
  wave=db.ReferenceProperty(Wave, required=True)
  host=db.ReferenceProperty(Participant, required=True)
  url=db.StringProperty(required=True)
  scratch=db.TextProperty()
  linkbot=db.StringProperty()

class Shard(db.Model):
  gadget=db.ReferenceProperty(Gadget, required=True)
  user=db.UserProperty(required=True)
  participant=db.ReferenceProperty(Participant)

class Attachment(db.Model):
  gadget=db.ReferenceProperty(Gadget, required=True)
  host=db.ReferenceProperty(Participant, required=True)
  blobid=blobstore.BlobReferenceProperty(required=True)

class Link(db.Model):
  gadget=db.ReferenceProperty(Gadget, required=True)
  host=db.ReferenceProperty(Participant, required=True)
  uri=db.StringProperty(required=True)

class AuthToken(db.Model):
  user=db.UserProperty(required=True)
  token=db.StringProperty(required=True)

class Invitation(db.Model):
  user=db.UserProperty(required=True)
  wave=db.ReferenceProperty(Wave, required=True)
  email=db.StringProperty(required=True)
