var db=null;
var doc=null;

function gotDoc(doc)
{
  log('got doc');
  log(doc);
  $('#doc').val(JSON.stringify(doc));

  fullDoc=doc;

//  renderEditor();
}

function saveDoc()
{
  log('saving parsed doc')
  var value=JSON.parse($('#doc').val());
  log(value);

  doc.save(value);
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

  doc.setDocCallback(gotDoc);
  doc.get();
}

$(document).ready(initDocument);