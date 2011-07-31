# -*- coding: utf-8 -*-
import io
import neighbors
import os
import sys #TODO: check PEP 366
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import others.ubigraph as ubigraph

def ubigraph_connect(clear=True):
    os.system('ubigraph_server -quiet &')
    time.sleep(1)
    U = ubigraph.Ubigraph()
    if clear: U.clear()
    return U

def class_to_color(clazz):
    COLORS = ["#ffff00", #Class F: Yellow
              "#ff0000", #Class B: Red
              "#00ff00", #Class C: Green
              "#0000ff"] #Class S: Blue
    return COLORS[int(clazz)]

def ubigraph_populate(neighbors, y, U=None):
    if not U: U = ubigraph_connect()
    nodes = []
    stylesVertices = [U.newVertexStyle(id=int(clazz) + 1, color=class_to_color(clazz), shape="sphere") for clazz in
                      sorted(set(y))]
    styleWrongEdge = U.newEdgeStyle(id=133, color="#ff0000", stroke="dashed")
    for i in range(len(neighbors)):
        nodes.append(U.newVertex(i, style=stylesVertices[int(y[i])]))
    for i in range(len(neighbors)):
        for nn in neighbors[i]:
            U.newEdge(nodes[i], nodes[int(nn)],
                      style=(styleWrongEdge if y[i] != y[int(nn)] else None))

def ubigraph_file(src, k=5):
    _, _, _, x, y = io.load_arff(src)
    ubigraph_data(x, y, k)

def ubigraph_data(x, y, k=5):
    ubigraph_populate(neighbors.nns(x, k), y)

PETECAN_ROOT = os.path.join(os.path.expanduser('~'), 'Proyectos', 'data', 'wikipedia-motifs')
ORIGINAL_DATA = os.path.join(PETECAN_ROOT, 'ArticleEgoMotifCounts.arff')
ubigraph_file(ORIGINAL_DATA)
