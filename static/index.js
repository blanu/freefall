function gotInvite(data)
{
  var url='/wave/join/'+data;
  $.post(url);
}

function addTab(data)
{
  log('addTab: '+data);

  $("#tabs").tabs('add', '/waves/'+data.id, data.name);
}

function delTab(data)
{
  log('delTab: '+data);

  $("#tabs > div > div").each(function(index, item) {
    log('checking '+item+' '+index+' '+$(item).attr('id'));
    if($(item).attr('id')==data)
    {
      log('removing tab '+index);
      $("#tabs").tabs('remove', index);
    }
  });
}

function renameTab(data)
{
  log('renameTab: '+data);
  for(var waveid in data)
  {
    name=data[waveid];
    log(name);

    var i=null;
    $('#'+waveid+'-label').text(name);
  }
}

function getContacts()
{
  log('get contacts');
  var url='/contacts';
  $.getJSON(url, gotContacts);
}

function gotContacts(contacts)
{
  log('got contacts');
  $('.contacts').empty();

  s='<table>';
  for(var x=0; x<contacts.length; x++)
  {
    s=s+'<tr><td>';
    if(typeof(contacts[x].image)!==undefined && contacts[x].image!=null && contacts[x].image!='null')
    {
      s=s+'<td><img src="'+contacts[x].image+'"/></td>';
    }
    else
    {
      s=s+'<td><img src="https://wave.google.com/wave/static/images/unknown.jpg"/></td>';
    }
    s=s+'<td><a class="addParticipantButton" href="#" addr="'+contacts[x].email+'">';
    if(typeof(contacts[x].title)!==undefined && contacts[x].title!=null && contacts[x].title!='null')
    {
      s=s+contacts[x].title;
    }
    else
    {
      s=s+contacts[x].email;
    }
    s=s+'</a></td></tr>';
  }
  s=s+'</table>'
  $('#addParticipantsFormTemplate .contacts').append(s);
}

function getInvites()
{
  log('get invites');
  var url='/invites';
  $.getJSON(url, gotInvites);
}

function gotInvites(invites)
{
  log('got invites');
  for(var x=0; x<invites.length; x++)
  {
    gotInvite(invites[x]);
  }
}

function initIndex()
{
  $("#tabs").tabs({'cache': true});
  $("#tabs").show();

  log('index listening');

  log('listening wave-'+ocean.userid+'-newtab');
  log('listening wave-'+ocean.userid+'-deltab');
  Web2Peer.listen('wave-'+ocean.userid+'-newtab', addTab);
  Web2Peer.listen('wave-'+ocean.userid+'-deltab', delTab);
  Web2Peer.listen('wave-'+ocean.userid+'-renametab', renameTab);
  Web2Peer.listen('user-'+ocean.userid+'-contacts', gotContacts);
  Web2Peer.listen('user-'+ocean.userid+'-invite', gotInvite);

  getContacts();
  getInvites();
}

$(document).ready(initIndex);