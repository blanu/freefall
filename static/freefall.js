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
  log('new Document '+db.dbid+' '+did);
  this.db=db;
  this.docid=did;
  this.fullDoc=null;

  this.docCallback=null;
  
  doc=this;

  this.internalDocCallback=function(data) {
		log('doc changed '+doc.docid);
		log(data);
		if(doc.docCallback)
		{
			doc.docCallback(doc, data);
		}
  }
  
  Web2Peer.listen(this.db.dbid+'-'+this.docid, this.internalDocCallback);

  this.setDocCallback=function(f)
  {
    this.docCallback=f;
  }

  this.get=function()
  {
    log('get doc');
    var url=this.base+'/db/'+this.db.dbid+'/'+this.docid;
    $.getJSON(url, this.internalDocCallback);
  }

  this.setName=function(name)
  {
		this.docid=name;
	}

  this.save=function(doc)
  {
		log('saving...');
    log(doc);

    this.fullDoc=doc;

    if(this.docid===null || this.docid===undefined)
    {
      var url=this.base+"/db/"+this.db.dbid;
      $.post(url, JSON.stringify(doc), this.setName);
		}
		else
		{
      var url=this.base+"/db/"+this.db.dbid+'/'+this.docid;
      $.post(url, JSON.stringify(doc));
		}
  }

  return this;
}

freefall.Database=function(base, id)
{
  log('new Database '+base+' '+id);
  this.base=base;
  this.dbid=id;

  this.docsCallback=null;

  this.setDocsCallback=function(f)
  {
    this.docsCallback=f;
  }

  this.getDocs=function()
  {
    log('get docs');
    var url=this.base+'/db/'+this.dbid;
    $.getJSON(url, this.docsCallback);
  }

  this.addDoc=function(docname)
  {
    log('dbname: '+docname);
    var url=this.base+"/db/"+this.dbid+'/'+docname;
    $.post(url, JSON.stringify(null));
  }

  this.get=function(docname)
  {
    return freefall.Document(this, docname);
  }

  return this;
}

freefall.submitForm=function()
{
	log('submitForm');
	log(this);

  var host=$(this).attr('host');
  var base='http://'+host;
	var dbname=$(this).attr('db');
	var db=freefall.Database(base, dbname);
	var docname=$(this).attr('doc');
	var doc=db.get(docname);
	
	var data={};
	$(this).find("input").each(function(index) {
		try
		{
  	  var key=$(this).attr('name');
	    var value=$(this).val();
	  
  	  data[key]=value;
		}
		catch(e)
		{
			log('Exception:');
			log(e);
		}
  });
	$(this).find("textarea").each(function(index) {
		try
		{
  	  var key=$(this).attr('name');
	    var value=$(this).val();
	  
  	  data[key]=value;
		}
		catch(e)
		{
			log('Exception:');
			log(e);
		}
  });
	
	doc.save(data);
	
	return false;
}

function initFreefall()
{
  Web2Peer.init("freefall");
  
  log('Installing magic forms...');
  log($('.freefall-form'));  
  $('.freefall-form').submit(freefall.submitForm);
}

$(document).ready(initFreefall);
