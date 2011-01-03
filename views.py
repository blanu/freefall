import logging
import urllib
from google.appengine.api import urlfetch
from mapreduce import context
from mapreduce import operation as op
from django.utils.simplejson import loads, dumps

from models import *

def process(entity):
  ctx=context.get()
  params=ctx.mapreduce_spec.mapper.params
  dbid=params['dbid']
  viewName=params['viewName']
  viewUrl=params['nodeUrl']+'/'+viewName

  logging.info('sending document to view: '+str(entity.state))
  form_fields = {"value": entity.state}
  form_data = urllib.urlencode(form_fields)
  result = urlfetch.fetch(url=viewUrl, payload=form_data, method=urlfetch.POST, headers={'Content-Type': 'application/x-www-form-urlencoded'})
  if result.status_code != 200:
    logging.error("Bad result: "+str(result.stats_code))
    return

  data=loads(result.content)
  logging.info('got view result: '+str(data))
  key=data['key']
  value=data['value']

  db=Database.all().filter("dbid =", dbid).get()
  if(db==None):
    loggin.error("No such database "+str(dbid))
    return

  view=View(database=db, viewid=viewName, viewkey=dumps(key), value=dumps(value))
  view.save()

