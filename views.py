import logging
import urllib
from google.appengine.api import urlfetch
from django.utils.simplejson import loads, dumps

from models import *

def map(doc, dbid, viewName, viewUrl):
  logging.info('sending document to view: '+str(doc.state))
  data=callNode(viewUrl, doc.state)

  if data!=None:
    logging.info('got view result: '+str(data))
    key=data['key']
    value=data['value']

    db=Database.all().filter("dbid =", dbid).get()
    if(db==None):
      logging.error("No such database "+str(dbid))
      return

    view=View(database=db, source=doc, viewid=viewName, viewkey=dumps(key), value=dumps(value))
    view.save()

def process(entity):
  ctx=context.get()
  params=ctx.mapreduce_spec.mapper.params
  dbid=params['dbid']
  viewName=params['viewName']
  viewUrl=params['nodeUrl']+'/'+viewName
  map(entity, dbid, viewName, viewUrl)
