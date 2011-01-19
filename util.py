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

from generic import TemplatePage, JsonPage, GenericPage, FilePage
from models import *

def notify(apikey, channel, msg):
  logging.debug('notify('+str(channel)+'): '+str(msg))

  fields={
    'apikey': apikey,
    'channel': channel,
    'data': msg
  }

  url='http://send.w2p.dtdns.net:9323/send'
  result=urlfetch.fetch(url, payload=urlencode(fields), method=urlfetch.POST)
  logging.debug('post result: '+str(result.status_code))

def sendMail(frm, to, subject, templateName, context):
  loader = CachingFileLoader("templates")

  templateNameHTML=templateName+".vm"
  templateHTML = loader.load_template(templateNameHTML)
  bodyHTML=templateHTML.merge(context, loader=loader)

  templateNamePlain=templateName+"_plain.vm"
  templatePlain = loader.load_template(templateNamePlain)
  bodyPlain=templatePlain.merge(context, loader=loader)

  #    resp.headers['Content-Type']='text/html'
  msg=mail.EmailMessage(sender=frm, to=to, subject=subject)
  msg.html=bodyHTML
  msg.body=bodyPlain

  msg.send()

def generateId():
  s=None
  if not (s and s[0].isalpha()):
    i=random.getrandbits(64)
    s=base64.urlsafe_b64encode(struct.pack('L', i))[:-1]
  while s[-1]=='A' or s[-1]=='=':
    s=s[:-1]

  return s

def newDatabase(owner, dbid=None):
  logging.error('nd dbid: '+str(dbid))
  if not dbid:
    logging.debug('no dbid')
    dbid=generateId()
    while Database.all().filter("dbid =", dbid).count()!=0:
      dbid=generateId()
  elif Database.all().filter("owner =", owner).filter("dbid =", dbid).count()!=0:
    return None

  logging.info('using '+str(dbid))
  db=Database(dbid=dbid, owner=owner)
  db.save()
  return db

def newDocument(db, state, docid=None):
  if not docid:
    docid=generateId()
    while Document.all().filter("docid =", docid).count()!=0:
      docid=generateId()
  elif Document.all().filter("docid =", docid).count()!=0:
    return None

  doc=Document(docid=docid, database=db, state=state)
  doc.save()
  return doc

def newSession(user):
  logging.error('ns user: '+str(user))
  sessionid=generateId()
  while Session.all().filter("sessionid =", sessionid).count()!=0:
      sessionid=generateId()

  logging.info('using '+str(sessionid))
  session=Session(user=user, sessionid=sessionid)
  session.save()
  return session

def listDocs(db):
  results=[]
  docs=Document.all().filter('database =', db).fetch(100)
  for rdoc in docs:
    results.append(rdoc.docid)

  logging.info('results: '+str(results))
  return results

def purgeViews(doc):
  logging.info('Purging views for '+str(doc))
  views=View.all().filter('source =', doc).fetch(100)
  for view in views:
    view.delete()
    
def runViews(nodeUrl, viewName, doc):
  pass
    
def loadConfig(db):
  configDoc=Document.all().filter("database =", db).filter("docid =", "_config").get()
  if not configDoc:
    return {}
  else:
    return loads(configDoc.state)
    
def resolveConfig(config, keys):
  value=config
  for key in keys:
    if key in value:
      value=value[key]
    else:
      return None
  return value
  
def callNode(url, params):
  logging.info('Calling node '+str(url)+' '+str(params))
  form_data = urllib.urlencode({"value": dumps(params)})
  try:
    result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST, headers={'Content-Type': 'application/x-www-form-urlencoded'})
  except:
    logging.error('Exception in fetch')
    return None
  if result.status_code != 200:
    logging.error("Bad result: "+str(result.status_code))
    return None

  data=loads(result.content)
  return data
  
