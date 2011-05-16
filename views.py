import logging
import urllib
from google.appengine.api import urlfetch
from google.appengine.ext import deferred
from django.utils.simplejson import loads, dumps
from jsonrpc import ServiceProxy

from models import *

dataBase='http://freefall.blanu.net/'
nodeUrl='http://blanu.net/viewMap/'

def purgeViews(doc):
  logging.info('Purging views for '+str(doc))
  views=View.all().filter('source =', doc).fetch(100)
  for view in views:
    view.delete()

def callNode(viewUrl, dataUrl):
  logging.info('Calling node '+str(url)+' '+str(params))
  url=viewUrl+"?data="+urllib.quote(dataUrl, '')
  try:
    result = urlfetch.fetch(url=url)
  except:
    logging.error('Exception in fetch')
    return None
  if result.status_code != 200:
    logging.error("Bad result: "+str(result.status_code))
    return None

  data=loads(result.content)
  return data

def runView(viewId, viewUrl, dbid, docid):
  logging.info('sending document to view: '+str(docid))
  dataUrl=dataBase+dbid+'/'+docid
  data=callNode(viewUrl, dataUrl)

  if data!=None:
    logging.info('got view result: '+str(data))
    key=data['key']
    value=data['value']

    db=Database.all().filter("dbid =", dbid).get()
    if db==None:
      logging.error("No such database "+str(dbid))
      return

    view=Database.all().ancestor(db).filter("dbid =", viewId).get()
    if view==None:
      logging.error("No such database "+str(viewId))
      return      

    s=ServiceProxy(dataBase+'db')
    s.modify([dbid, viewId], [
      ['add', [key, value]]
    ])
      
def runViews(doc, views):
  for view in views:
    deferred.defer(runView, view.dbid, view.viewUrl, doc.dbid, doc.docid)
