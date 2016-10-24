/* display the datatable */
function showTable (){

  /* check for url parameter */
  if (window.location.href.indexOf('?') != -1) {
    var rest=window.location.href.split('?')[1];
    var elms = rest.split('&');
    var parms = {};
    for (var i=0,elm; elm=elms[i]; i++) {
      elm12 = elm.split('=');
      parms[elm12[0]] = elm12[1];
    }  
  }
  else {
    var parms = {};
  }


  if ('stanza' in parms) {
    showPoem(parms['stanza'].split('.')[0], parms['stanza']);
    var searchterm='';
    if ('break' in parms) {
      if (parms['break']) {
	return;
      }
    }
  }
  else if ('char' in parms) {
    var searchterm = parms['char'];
  }
  else {
    var searchterm = '';
  }
  
  var txt = '<table id="datatable"></table>';
  var idx = 1;
  var stanza = '0';
  for (var i=0,row; row=CHARS[i]; i++) {
    if (row[9] != stanza) {
      stanza = row[9];
      idx = 1;
    }
    /* activate change when clicking on poem */
    CHARS[i][10] = idx; //.push(idx);
    CHARS[i][8] = '<span style="cursor:pointer;color:blue;" onclick="showPoem('+row[8]+',\''+row[9]+'\','+row[10]+')">'+row[8]+'</span>';
    idx += 1
  }
  document.getElementById('data').innerHTML = txt;

  var dtable = $('#datatable').dataTable( {
    "data" : CHARS,
    "columns" : [
      {"title" : "", "class" : "number-table", "searchable" : false},
      {"title" : "HANZI", "class" : "description-table"},
      {"title" : "PINYIN", "class" : "description-table"},
      {"title" : "GLOSS", "class" : "description-table"},
      {"title" : "MCH", "class" : "description-table"},
      {"title" : "OCBS", "class" : "description-table"},
      {"title" : "OCPWY", "class" : "description-table"},
      {"title" : "GSR", "class" : "description-table"},
      {"title" : "POEM", "class" : "description-table"},
      {"title" : "STANZA", "class" : "description-table"},
      {"title" : "SECTION", "class" : "description-table"},
    ],
    search : {search : decodeURIComponent(searchterm)}
  });


}


function showPoem(number, this_stanza, this_idx) {
  
  var data = POEMS[number];
  var txt = '';
  txt += '<h3></h3>';
  txt += '<table id="rhymetable"><tr><th>SECTION</th><th>RHYME</th><th>ALT. RHY.</th><th>OCBS</th><th>PWY</th><th>MCH</th><th>YUN</th></tr>';
  var rhymes = {};
  var colors = ['lightblue','lightgray','lightgreen','lightyellow','lightred',
    'Gold','LightPink','BurlyWood','RosyBrown','DarkGray','Cyan','SandyBrown'];
  for (var i=0,row; row=data['sections'][i]; i++) {
    var sta = row[0];
    if (row[2] != '') {
      if (sta in rhymes) {
        if (rhymes[sta].indexOf(row[2]) == -1) {
          rhymes[sta].push(row[2]);
        }
      }
      else {
        rhymes[sta] = [row[2]];
      }
    }
  }
  console.log('rhymes',rhymes);


  var idx = 1;
  /* start doing the table iteration */
  var stanza = '';
  for (var i=0,row; row=data['sections'][i]; i++) {
    

    var sec = row[1];
    var sta = row[0]
    var rhy = row[2];
    var ary = row[3];
    var obs = row[4];
    var pwy = row[5];
    var mch = row[6];
    var yun = row[7];
    var chr = row[8];


    if (stanza != sta) {
      if (sta == this_stanza) {
	txt += '<tr><td colspan="9" style="font-weight:bold;border:2px solid black;">';
      }
      else {
	txt += '<tr><td colspan="9">';
      }
      txt += sta+'</td></tr>';
      stanza = sta;
      var idx = 1;
    }

    if (idx == this_idx && stanza == this_stanza) {
      var this_col = '2px solid black';
    }
    else {
      this_col = '1px solid lightgray';
    }
    
    txt += '<tr>';
    idx += 1;



    /* assemble rhymes */
    if (rhy != '') {
      var col = colors[rhymes[sta].indexOf(rhy)];
      sec = sec.replace(RegExp(chr,'g'),'<span style="background-color:'+col+';">'+chr+'</span>');
      yun = yun.replace(yun,'<span style="background-color:'+col+';">'+yun+'</span>');
    }
    else {
      var col = 'white';
    }

    txt += '<td style="border:'+this_col+'">'+sec+'</td>';
    txt += '<td style="border:'+this_col+';background-color:'+col+';">'+rhy+'</td>';
    txt += '<td style="border:'+this_col+'">'+ary+'</td>';
    txt += '<td style="border:'+this_col+'">'+obs+'</td>';
    txt += '<td style="border:'+this_col+'">'+pwy+'</td>';
    txt += '<td style="border:'+this_col+'">'+mch+'</td>';
    txt += '<td style="border:'+this_col+'">'+yun+'</td>';

    txt += '</tr>';
  }
  txt += '</table>';

  var falert = document.createElement('div');
  falert.id = 'fake';
  falert.className = 'fake_alert';
  var text = '<div class="message" style="background:lightgray"><p class="head">Shijing '+number+' ('+data['name']+')</p>';
  text += '<button onclick="$(\'#fake\').remove();showPoem('+(number-1)+')">PREVIOUS POEM</button>';
  text += '<button onclick="$(\'#fake\').remove()">CLOSE</button>';
  text += '<button onclick="$(\'#fake\').remove();showPoem('+(number+1)+')">NEXT POEM</button>';
  text += '<p>'+txt+'</p>';
  text += '</div>';
  document.body.appendChild(falert);
  falert.innerHTML = text;
}
