from lingpy import *
import networkx as nx
from lingpy.thirdparty import linkcomm as lc
from sys import argv
from collections import Counter
import markdown
import pickle


try:
    I = pickle.load(open('R_infomap.bin','rb'))
    print('[i] loaded graph')
except:

    # load any graph version, let's take the simple one for the moment
    I = nx.read_yaml('R_infomap.yaml')
    with open('R_infomap.bin', 'wb') as f:
        pickle.dump(I, f)

# open and analyze the infomap graph
#I = nx.read_yaml('R_infomap.yaml')
D = {}
for nA, data in I.nodes(data=True):

    imp = data['infomap']
    _data = ['rime','occurrence','certainty','shangsheng','reading','mch', 'stanza']

    try:
        D[imp] += [(nA,)+tuple([data[x] for x in _data])]
    except KeyError:
        D[imp] = [(nA,)+tuple([data[x] for x in _data])]


tpl = """<tr>
  <td style="border: 1px solid lightgray;"><a
  style="text-decoration:none;color:Crimson;" target="other" href="http://dighl.github.io/shijing/index.html?char={0}">{0}</a></td>
  <td style="border: 1px solid lightgray;">{1}</td>
  <td style="border: 1px solid lightgray;">{2}</td>
  <td style="border: 1px solid lightgray;">{3}</td>
  <td style="border: 1px solid lightgray;">{4}</td>
</tr>"""
tps = """<a style="text-decoration:none;color:cornflowerblue;" target="other"
href="http://dighl.github.io/shijing/index.html?stanza={0}&break=break&char={1}">{0}</a>"""
tpt = """
<table id="table_{1}" style="border:2px solid black;display: none;">
  <tr>
    <th onclick="sort_table(0,'table_{1}', 0);" style="cursor:pointer;border: 1px solid gray;">Character</th>
    <th onclick="sort_table(1,'table_{1}', 0);" style="cursor:pointer;border: 1px solid gray;">Middle Chinese</th>
    <th onclick="sort_table(2,'table_{1}', 0);" style="cursor:pointer;border: 1px solid gray;">Old Chinese</th>
    <th onclick="sort_table(3,'table_{1}', 0);" style="cursor:pointer;border: 1px solid gray;">Occurrence</th>
    <th style="border: 1px solid gray; max-width:500px;">Stanza</th>
  </tr>
  {0}
</table>"""


with open('R_stats_infomap.tsv', 'w') as f:
    most_coms = []
    txt = ''
    for idx in sorted(D, key=lambda x: len(D[x]), reverse=True):
        rimes = [line[1] if line[1] else '?' for line in D[idx]]
        rimeset = sorted(set(rimes), key=lambda x: rimes.count(x),
                reverse=True)


        # make a dictionary sorting
        tmp = {}
        for line in D[idx]:
            rime = line[1] if line[1] else '?'
            
            if 'ʔ' in line[4]:
                rime = rime + 'ʔ'
            if line[3] == '?':
                rime = rime + '[?]'
            
            try:
                tmp[rime] += [tuple(line)]
            except KeyError:
                tmp[rime] = [tuple(line)]

        # write stuff to file
        sorted_data = sorted(tmp.items(), key=lambda x: len(x[1]),
                reverse=True)
        print(sorted_data[0][1],len(sorted_data[0][1]))
        best_char = sorted_data[0][0]
        txt2 = ''
        txt2 += '<h3>Community {0} (ID: {1}, Members: {2})</h3>\n<ul>'.format(
                best_char, 
                idx+1,
                sum([len(x[1]) for x in sorted_data]))

        for k,v in sorted_data:
            # prepare text3
            txt3 = ''
            for line in sorted(v, key=lambda x: x[1], reverse=True):
                txt3 += tpl.format(
                        line[0],
                        line[6],
                        line[5].replace(' ','') + str('<sup>'+line[3]+'</sup>' if line[3] == '?' else ''),
                        line[2],
                        ', '.join([tps.format(x,line[0]) for x in line[-1].split(',')])
                        )
            txt3 = tpt.format(txt3, str(idx+1)+'_'+k)
          
            txt2 += """<li style="display:flex;" id="cluster_{3}"><b style="width:150px!important;">-{0}</b>
            <span style="width:150px">Occurrence: {1}</span> <span
            style="border:1px solid
            black;background:Crimson;cursor:pointer;color:white;font-weight:bold;" id="span_{3}"
onclick="toggle_table('{3}');">SHOW</span> </li> \n{2}""".format(
                    k, len(v), txt3,
                    str(idx+1)+'_'+k
                    )
        txt2 += '</ul>\n'

        txt += '<div id="community_'+str(idx+1)+'">'+txt2+'</div>'
        
        # write cluster to file
        f.write('# '+rimeset[0]+' / {0} / {1}\n'.format(
            idx,
            len(rimes)
            ))
        for elm in rimeset:
            f.write('  '+elm+'\t'+str(rimes.count(elm))+'\n')

        f.write('\n')
        most_coms += [(idx,elm)]
 
head = '<html><head><meta charset=utf8 /></head><body>{1}<div id="mainpart">{0}</div></body></html>'
title = '<h1>Infomap Community Detection Analysis</h1>'
title += """
Type in the keywords you wish to search for, type 
<pre><code>community=1,2,3,5</code></pre> in order to search for specific
communities by their ID.
Type
<pre><code>characters=我，你</code></pre> 
in order to search for communities containing certain characters, and type
<pre><code>rimes=ak,a</code></pre> 
in order to limit the search to specific rime groups.<br>
"""
title += '<script src="T_community.js"></script>'
title += '<input id="textfield" type="text" placeholder="filter by community" style="width:200px" /><input id="click" onclick="filterCommunities({cnum})" type="button" value="OK" />'.format(cnum=len(D)+1)


with open('R_infomap.html', 'w') as f:
    f.write(head.format(txt, title))


        


