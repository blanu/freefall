import re
import logging
import random
import base64
import struct
import time

import urllib
from urllib import urlencode, unquote_plus

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.api import mail
from django.utils.simplejson import loads, dumps

from airspeed import CachingFileLoader

from generic import JsonPage
from models import *
from util import *

class NewDatabasePage(JsonPage):
  def processJson(self, method, user, req, resp, args, obj):
    logging.info('new database')
    logging.info(obj)
    if obj:
      try:
        dbid=obj['dbid']
      except:
        dbid=None
    else:
      dbid=None

    logging.info('dbid: '+str(dbid))

    try:
      db=newDatabase(user, dbid=dbid)
    except Exception, e:
      logging.error(str(e))
    if not db:
      logging.error('Database with that id already exists '+str(dbid))
      return None
    else:
      logging.error('db: '+str(db))
      logging.info('dbid: '+str(db.dbid))

      dbs=Database.all().filter("owner =", user).fetch(100)
      results=[]
      for rdb in dbs:
        results.append(rdb.dbid)

      logging.info('results: '+str(results))

      notify('freefall', 'dbs-'+user.email().lower(), dumps(results))

      return db.dbid

  def requireLogin(self):
    return True

class DatabasesPage(JsonPage):
  def processJson(self, method, user, req, resp, args, obj):
    dbs=Database.all().filter("owner =", user).fetch(100)
    results=[]
    for db in dbs:
      results.append(db.dbid)

#    notify('freefall', 'dbs-'+user.email().lower()+'-newtab', dumps({'name': name, 'id': wave.waveid}))

    return results

  def requireLogin(self):
    return True

class DatabasePage(JsonPage):
  def processJson(self, method, user, req, resp, args, obj):
    dbid=args[0]

    db=Database.all().filter("dbid =", dbid).get()
    if not db:
      logging.error('Database with that id does not exist '+str(dbid))
      return

    if method=='GET':
#    notify('freefall', 'dbs-'+user.email().lower()+'-newtab', dumps({'name': name, 'id': wave.waveid}))

      results=[]
      docs=Document.all().filter("database =", db).fetch(100)
      for doc in docs:
        results.append(doc.docid)

      return results
    elif method=='POST':
      doc=newDocument(db, dumps(obj))
      if not doc:
        logging.error('Document id collision '+str(docid)+', overwriting...')
        doc.state=dumps(obj)
        doc.save()
        return None
      else:
        doc.save()
        docs=Document.all().filter('database =', db).fetch(100)
        results=[]
        for rdoc in docs:
          results.append(rdoc.docid)

        logging.info('results: '+str(results))

        notify('freefall', db.dbid, dumps(results))

        return doc.docid
    else:
      logging.error('Unknown method '+str(method))

  def requireLogin(self):
    return False

class DocumentPage(JsonPage):
  def processJson(self, method, user, req, resp, args, obj):
    logging.info('document')
    logging.info(method)

    dbid=args[0]
    docid=args[1]

#    db=Database.all().filter("owner =", user).filter("dbid =", dbid).get()
    db=Database.all().filter("dbid =", dbid).get()
    if not db:
      logging.error('Database with that id does not exist '+str(dbid))
      return None

    if method=='GET':
      doc=Document.all().filter("database =", db).filter('docid =', docid).get()
      if not doc:
        logging.error('Document with that id does not exist '+str(docid))

        config=loadConfig(db)
        logging.info('config: '+str(config))
        baseUrl=resolveConfig(config, ['node'])
        logging.info('baseUrl: '+str(baseUrl))
        errorHandler=resolveConfig(config, ['error', 'notFound'])
        logging.info('errorHandler: '+str(errorHandler))
        if baseUrl and errorHandler:
          callNode(baseUrl+'/'+errorHandler, docid)

        return None
      if not doc.state:
        return None
      else:
        return loads(doc.state)
    elif method=='POST':
      doc=newDocument(db, dumps(obj), docid=docid)
      if not doc:
        logging.error('Document id collision '+str(docid)+', overwriting...')
        doc=Document.all().filter("docid =", docid).get()
        logging.error('state: '+str(doc.state))
        doc.state=dumps(obj)
        doc.save()
        logging.error('new state: '+str(doc.state))
        notify('freefall', db.dbid+'-'+doc.docid, doc.state) # No need to dumps, already string

        purgeViews(doc)

        return doc.docid
      else:
        logging.debug('notifying')
        notify('freefall', db.dbid, dumps(listDocs(db)))
        logging.debug('notified')

        return doc.docid
    else:
      logging.error('Unknown method '+str(method))

  def requireLogin(self):
    return False

class DeleteDocumentPage(JsonPage):
  def processJson(self, method, user, req, resp, args, obj):
    logging.info('document')
    logging.info(method)

    dbid=args[0]
    docid=args[1]

#    db=Database.all().filter("owner =", user).filter("dbid =", dbid).get()
    db=Database.all().filter("dbid =", dbid).get()
    if not db:
      logging.error('Database with that id does not exist '+str(dbid))
      return None

    doc=Document.all().filter("docid =", docid).get()
    if not doc:
      logging.error('No doc to delete '+str(docid))
    else:
      doc.delete()
      purgeViews(doc)

    logging.debug('notifying')
    notify('freefall', db.dbid, dumps(listDocs(db)))
    logging.debug('notified')

  def requireLogin(self):
    return False

class ViewPage(JsonPage):
  def processJson(self, method, user, req, resp, args, obj):
    dbid=args[0]
    viewid=args[1]
    key=req.get('key', None) # Key should already be in JSON encoding, so we can compare directly
    logging.info("key: "+str(key))

    viewdb=Database.all().filter("dbid =", dbid).get()
    if not viewdb:
      logging.error('Database with that id does not exist '+str(dbid))
      return None

    if method=='GET':
      results=[]
      if(key==None):
        views=View.all().filter("database =", viewdb).filter('viewid =', viewid).fetch(100)
      else:
        logging.info(str(db.GqlQuery("SELECT * FROM View WHERE database = :1 AND viewid = :2", viewdb, viewid).fetch(100)[0].viewkey))
        logging.info(str(db.GqlQuery("SELECT * FROM View WHERE database = :1 AND viewid = :2 and viewkey = :3", viewdb, viewid, key).fetch(100)))
        logging.info(str(key))
        views=db.GqlQuery("SELECT * FROM View WHERE database = :1 AND viewid = :2 and viewkey = :3", viewdb, viewid, key).fetch(100)

      if not views:
        logging.error('View with that id does not exist or is empty '+str(viewid))
        return {'viewid': viewid, 'viewkey': loads(key), 'results': results}
      for view in views:
        if view.value!=None:
          value=loads(view.value)
          results.append(value)
      return {'viewid': viewid, 'viewkey': loads(key), 'results': results}

  def requireLogin(self):
    return False

class AllPage(JsonPage):
  def processJson(self, method, user, req, resp, args, obj):
    dbid=args[0]

    db=Database.all().filter("dbid =", dbid).get()
    if not db:
      logging.error('Database with that id does not exist '+str(dbid))
      return None


    if method=='GET':
      return getDocs(db)

  def requireLogin(self):
    return False
