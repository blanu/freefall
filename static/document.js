var db=null;
var doc=null;

function gotDoc(doc, data)
{
  log('got doc');
  log(data);
  
//  $('#doc').val(JSON.stringify(data));
  $('#doc').each(function() {
		this.bespin.editor.value=JSON.stringify(data);
	});
  
  fullDoc=data;

//  renderEditor();

//  bespin.useBespin('doc').then(function(env) {
//		editor=env.editor;
//	});
}

function saveDoc()
{
  log('saving parsed doc')
//  var value=$('#doc').val();
  var value=null;
  $('#doc').each(function() {
		value=this.bespin.editor.value;
	});
  log(value);

  if(jsonlint.parse(value))
  {
    value=JSON.parse(value);
    doc.save(value);
    $('#doc').val(JSON.stringify(value, null, '  '));
  }
  else
  {
    log('Invalid json: '+value);
  }
}

function initBespin()
{
  doc.setDocCallback(gotDoc);
  doc.get();	
}

function initDocument()
{
  log('initDocument: '+dbid+' '+docid);
  $("#tabs").tabs();
  log('initDocument: '+dbid+' '+docid);

  db=freefall.Database('', dbid);
  doc=db.get(docid);

  log('listening doc-'+userid+'-'+dbid+'-'+docid);
  Web2Peer.listen('doc-'+userid+'-'+dbid+'-'+docid, gotDoc);

  $('#saveDoc').click(saveDoc);
  log('button: ');
  log($('#saveDoc'));

//  $('input[name="type"]').change(changeType);

  window.onBespinLoad=initBespin;
}

$(document).ready(initDocument);
