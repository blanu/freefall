var db=freefall.Database('', dbid);

function gotDocs(docs)
{
  log('got docs');
  log(docs);
  $('#docs').empty();
  if(docs!=null)
  {
    for(var x=0; x<docs.length; x++)
    {
      $('#docs').append('<li><a class="doclink" href="/dashboard/'+dbid+'/'+docs[x]+'">'+docs[x]+'</a></li>');
    }
  }
}

function addDbDialog()
{
  $("#addDbDialog").dialog({
    buttons: {
      "Add": function() {
        var dbname=$("#addDbNameField").val();
        log('addDoc call: '+dbname);
        log(db);
        log(db.addDoc);
        db.addDoc(dbname);
        $(this).dialog("close");
      },
      "Cancel": function() {
        $(this).dialog("close");
      }
    }
  });

  return false;
}

function initDatabase()
{
  log('listening docs-'+userid+'-'+dbid);
  Web2Peer.listen('docs-'+userid+'-'+dbid, gotDocs);

  $("#addDbButton").click(addDbDialog);

  db.setDocsCallback(gotDocs);
  db.getDocs();
}

$(document).ready(initDatabase);
