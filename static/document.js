var fullDoc=null;

function getDoc()
{
  log('get doc');
  var url='/db/'+dbid+'/'+docid;
  $.getJSON(url, gotDoc);
}

function gotDoc(doc)
{
  log('got doc');
  log(doc);
  $('#doc').val(JSON.stringify(doc));

  fullDoc=doc;

  renderEditor();
}

function saveDoc()
{
  var doc=$('#doc').val();

  fullDoc=doc;

  var url="/db/"+dbid+'/'+docid;
  $.post(url, doc);
}

function initDocument()
{
  $("#tabs").tabs();

  log('listening doc-'+userid+'-'+dbid+'-'+docid);
  Web2Peer.listen('doc-'+userid+'-'+dbid+'-'+docid, gotDoc);

  $('#saveDoc').click(saveDoc);

  $('input[name="type"]').change(changeType);

  getDoc();
}

$(document).ready(initDocument);
