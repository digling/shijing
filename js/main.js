/* display the datatable */
function showTable (){
  
  var txt = '<table id="datatable"></table>';
  for (var i=0,row; row=CHARS[i]; i++) {
    /* activate change when clicking on poem */
    CHARS[i][8] = '<span style="cursor:pointer;color:blue;" onclick="showPoem('+row[8]+')">'+row[8]+'</span>';
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
    ]
  });
}


function showPoem(number) {
  
  var data = POEMS[number];
  var txt = '';
  txt += '<h3></h3>';
  txt += '<table id="rhymetable"><tr><th>SECTION</th><th>RHYME</th><th>ALT. RHY.</th><th>OCBS</th><th>PWY</th><th>MCH</th><th>YUN</th></tr>';
  var rhymes = {};
  var colors = ['lightblue','lightgray','lightgreen','lightyellow','lightred'];
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

  /* start doing the table iteration */
  var stanza = '';
  for (var i=0,row; row=data['sections'][i]; i++) {
    txt += '<tr>';
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
      txt += '<td colspan="9">'+sta+'</td></tr><tr>';
      stanza = sta;
    }

    /* assemble rhymes */
    if (rhy != '') {
      var col = colors[rhymes[sta].indexOf(rhy)];
      sec = sec.replace(RegExp(chr,'g'),'<span style="background-color:'+col+';">'+chr+'</span>');
      yun = yun.replace(yun,'<span style="background-color:'+col+';">'+yun+'</span>');
    }
    else {
      var col = 'white';
    }

    txt += '<td>'+sec+'</td>';
    txt += '<td style="background-color:'+col+';">'+rhy+'</td>';
    txt += '<td>'+ary+'</td>';
    txt += '<td>'+obs+'</td>';
    txt += '<td>'+pwy+'</td>';
    txt += '<td>'+mch+'</td>';
    txt += '<td>'+yun+'</td>';

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
