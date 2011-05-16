from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import blobstore

class Database(db.Model):
  dbid=db.StringProperty(required=True)
  depends=db.SelfReferenceProperty()
  viewUrl=db.StringProperty()
  version=db.StringProperty()

class Document(db.Model):
  docid=db.StringProperty(required=True)
  database=db.ReferenceProperty(Database, required=True)
#  participant=db.ReferenceProperty(Participant)
  state=db.TextProperty()
  depends=db.SelfReferenceProperty()
  version=db.StringProperty()

class View(db.Model):
  database=db.ReferenceProperty(Database, required=True)
  source=db.ReferenceProperty(Document, required=True)
  viewid=db.StringProperty(required=True)
  viewkey=db.StringProperty(required=True)
  value=db.TextProperty(required=True)
  
class Session(db.Model):
  user=db.UserProperty(required=True)
  sessionid=db.StringProperty(required=True)
