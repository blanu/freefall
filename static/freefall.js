function _ajax_request(url, data, callback, type, method) {
    if (jQuery.isFunction(data)) {
        callback = data;
        data = {};
    }
    return jQuery.ajax({
        type: method,
        url: url,
        data: data,
        success: callback,
        dataType: type
        });
}

jQuery.extend({
    put: function(url, data, callback, type) {
        return _ajax_request(url, data, callback, type, 'PUT');
    },
    delete_: function(url, data, callback, type) {
        return _ajax_request(url, data, callback, type, 'DELETE');
    }
});

freefall={};

$(function() {
  getFreefall = function()
  {
    return freefall;
  };
});

freefall.Document=function(db, did)
{
  this.db=db;
  this.docid=did;
  this.fullDoc=null;

  this.docCallback=null;

  this.setDocCallback=function(f)
  {
    this.docCallback=f;
  }

  this.get=function()
  {
    log('get doc');
    var url='http://blanu.net:8080/db/'+this.db.dbid+'/'+this.docid;
    $.getJSON(url, this.docCallback);
  }

  this.save=function(doc)
  {
    log(doc);

    this.fullDoc=doc;

    var url="http://blanu.net:8080/db/"+this.db.dbid+'/'+this.docid;
    $.post(url, JSON.stringify(doc));
  }

  return this;
}

freefall.Database=function(dbid)
{
  this.dbid=dbid;

  this.docsCallback=null;

  this.setDocsCallback=function(f)
  {
    this.docsCallback=f;
  }

  this.getDocs=function()
  {
    log('get docs');
    var url='http://blanu.net:8080/db/'+this.dbid;
    $.getJSON(url, this.docsCallback);
  }

  this.addDoc=function(docname)
  {
    log('dbname: '+docname);
    var url="http://blanu.net:8080/db/"+dbid+'/'+docname;
    $.post(url, JSON.stringify(null));
  }

  this.get=function(docname)
  {
    return freefall.Document(this, docname);
  }

  return this;
}

function initFreefall()
{
  Web2Peer.init("freefall");
}

$(document).ready(initFreefall);
