function filterCommunities(cnum) {
  
  var ipt = document.getElementById('textfield');
  var values;

  var val = ipt.value;
  if (val.indexOf('community') != -1) {
    var values = val.split(/[:=]/)[1].split(/\s*,\s*/);

    try {
      for (var i=0,val; val=values[i]; i++) {
	values[i] = parseInt(values[i]);
      }
    }
    catch(e) {
      values = [];
      for (var i=1; i<cnum; i++) {
	values.push(i);
      }
    }

    if (values.length == 0 || isNaN(values[0])){
      values = [];
      for (var i=1; i<cnum; i++) {
	values.push(i);
      }
    }
  }
  else if (val == '') {
    values = [];
      for (var i=1; i<cnum; i++) {
	values.push(i);
      }
  }
  else if (val.indexOf('character') != -1) {

    var chars = val.split(/[:=]/)[1].split(/\s*,\s*/);
    values = [];
    for (var i=1; i < cnum; i++) {
      var txt = document.getElementById('community_'+i);
      for (var j=0,this_char; this_char = chars[j]; j++) {
	if (txt.innerHTML.indexOf(this_char) != -1) {
	  values.push(i);
	}
      }
    }
  }
  else if (val.indexOf('rime' != -1 || val.indexOf('rimes') != -1)) {

    var chars = val.split(/[:=]/)[1].split(/\s*,\s*/);
    values = [];
    for (var i=1; i < cnum; i++) {
      var txt = document.getElementById('community_'+i);
      for (var j=0,this_char; this_char = chars[j]; j++) {
	if (txt.innerHTML.indexOf('-'+this_char+'<') != -1) {
	  values.push(i);
	}
      }
    }
  }


  for (var i=1;i<cnum; i++) {
    if (values.indexOf(i) == -1) {
      document.getElementById('community_'+i).style.display = 'none';
    }
    else {
      document.getElementById('community_'+i).style.display = 'block';
    }
  }
}


function toggle_table(idx) {

  var elm = document.getElementById('table_'+idx);
  if (elm.style.display == 'none') {
    elm.style.display = 'block';
    document.getElementById('span_'+idx).innerHTML = 'HIDE';
  }
  else if (elm.style.display == 'block') {
    elm.style.display = 'none';
    document.getElementById('span_'+idx).innerHTML = 'SHOW';
  }
}

function sort_table (idx, idf, dir) {

  if (dir == 1) {
    var new_dir = 0;
  }
  else {
    var new_dir = 1;
  }
  
  var table = document.getElementById(idf);
  var rows = [];
  for (var i=1,row; row=table.rows[i]; i++) {
    rows.push(row);
  }
  //console.log(rows);
  rows.sort(function (x,y) {
    console.log(x.cells[idx]);
    console.log(x.cells[idx].innerHTML);
    if (idx < 3) {
    if (dir == 0) {
      return x.cells[idx].innerHTML.localeCompare(y.cells[idx].innerHTML);
    }
    else {
      return y.cells[idx].innerHTML.localeCompare(x.cells[idx].innerHTML);
    }}
    else {
      if (dir == 0) {
	return parseInt(x.cells[idx].innerHTML) - parseInt(y.cells[idx].innerHTML);
      }
      else {
	return parseInt(y.cells[idx].innerHTML) - parseInt(x.cells[idx].innerHTML);
      }
    }

  });
  var txt = '';
  txt += '<tr>'+table.rows[0].innerHTML+'</tr>';
  for (var i=0,row;row=rows[i]; i++) {
    txt += '<tr>'+rows[i].innerHTML+'</tr>';
  }
  
  table.innerHTML = txt; 
  table.rows[0].cells[idx].onclick = function() {sort_table(idx, idf, new_dir);};

}
