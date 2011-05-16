import logging

from google.appengine.ext import db as dblib

from generic import JsonRpcService
from models import *
from util import *

from views import *

class DatabaseService(JsonRpcService):
  def json_new(self, dbid):
    logging.info('new database:' +str(dbid))

    if Database.all().filter("dbid =", dbid).count()!=0:
      logging.error('Database with that id already exists '+str(dbid))
      return None

    logging.info('using '+str(dbid))
    db=Database(dbid=dbid)
    db.save()
    
    return db.dbid
  
  def json_list(self):
    dbs=Database.all().fetch(100)
    results=[]
    for db in dbs:
      results.append(db.dbid)

    return results

  def json_keys(self, dbid):
    db=lookupDb(dbid)
    if not db:
      logging.error('Database with that id does not exist '+str(dbid))
      return

    results=[]
    docs=Document.all().filter("database =", db).fetch(100)
    for doc in docs:
      results.append(doc.docid)

    return results

  def json_docs(self, dbid):
    db=lookupDb(dbid)
    if not db:
      logging.error('Database with that id does not exist '+str(dbid))
      return None

    return getDocs(db)

class DocumentService(JsonRpcService):
  def json_get(self, dbid, docid):
    db=lookupDb(dbid)    
    if not db:
      logging.error('Database with that id does not exist '+str(dbid))
      return None

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
    
  def json_modify(self, dbid, changes):
    db=lookupDb(dbid)
    if not db:
      logging.error('Database with that id does not exist '+str(dbid))
      return None
    
    dblib.run_in_transaction(self.applyChanges, db, changes)

  def applyChanges(self, db, changes):
    ops={'add': self.addChange, 'del': self.delChange, 'mod': self.modChange}
    
    for op, params in changes:
      if op in ops:
        f=ops[op]
        f(db, *params)
      else:
        raise(Exception('Invalid op: '+str(op)))    

  def addChange(self, db, docid, data):    
    if not docid:
      docid=generateId()
      while Document.all().ancestor(db).filter("docid =", docid).count()!=0:
        docid=generateId()
    elif Document.all().ancestor(db).filter("docid =", docid).count()!=0:
      logging.error('add docid collision: '+str(docid))
      return None

    doc=Document(parent=db, docid=docid, database=db, state=dumps(data))
    doc.save()

    views=Database.all().ancestor(db).filter("depends =", db).fetch(100)
    runViews(doc, views)
        
    return doc.docid

  def delChange(self, db, docid, path, version):
    logging.info('document')

    doc=Document.all().ancestor(db).filter("docid =", docid).get()
    if not doc:
      logging.error('No doc to delete '+str(docid))
      return False
    
    doc.delete()
#      purgeViews(doc)

    return True

  def modChange(self, db, docid, path, version, data):
    doc=Document.all().ancestor(db).filter("docid =", docid).get()
    if not doc:
      logging.error('No such doc to modify: '+str(docid))
      return False

    if version and doc.version!=version:
      raise(Exception('Version mismatch: '+str(version)+' != '+str(doc.version)))
      
    doc.state=dumps(data)
    doc.save()
    
#    purgeViews(doc)
#    runView(doc);
      
    return True
          
class ViewService(JsonRpcService):
  def json_new(self, dbid, viewId, viewUrl):

    logging.info('new view:' +str(viewId)+' of '+str(dbid))

    db=Database(parent=db, dbid=viewId, depends=db, viewUrl=viewUrl)
    db.save()
    
    return db.dbid    
