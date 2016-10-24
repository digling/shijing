import networkx as nx
import pickle
import random

try:
    graph = pickle.load(open('R_infomap.bin','rb'))
    print('[i] loaded graph')
except:

    # load any graph version, let's take the simple one for the moment
    graph = nx.read_yaml('R_infomap.yaml')
    with open('R_infomap.bin', 'wb') as f:
        pickle.dump(graph, f)

# assemble subgraphs
subs = {}
for n,data in graph.nodes(data=True):

    col = data['color']
    try:
        subs[col] += [n]
    except KeyError:
        subs[col] = [n]

ccol = {
        'red' : 'ə',
        'green' : 'a',
        'blue' : 'u',
        'gray' : 'e',
        'yellow' : 'i',
        'cyan' : 'o'
        }

for s in sorted([x for x in subs if x not in '']):
    subg = nx.subgraph(graph, subs[s])
    nInt = len(subg.edges())
    
    nExt = 0
    for n in sorted(subs[s]):
        
        for nB in graph.edge[n]:
            if nB in subg:
                pass
            else:
                nExt += 1
    print(ccol[s], '\t', '{0:.2f}'.format(nExt / (nExt + 2 * nInt)))

# compute random conductance
cons = [0 for i in range(6)]
for i in range(100):
    
    nodes = list(graph.nodes())

    for j,s in enumerate(sorted([x for x in subs if x not in ''])):
        nnodes = random.sample(nodes, len(subs[s]))

        nExt = 0
        nInt = 0
        for n in nnodes:
            for nB in graph.edge[n]:
                if nB in nnodes:
                    nInt += 1
                else:
                    nExt += 1
        c = nExt / (nExt + 2 * nInt)
        cons[j] += c
print('')
for i,c in enumerate(cons):
    print(i+1, '\t', '{0:.2f}'.format(c / 100))
        

