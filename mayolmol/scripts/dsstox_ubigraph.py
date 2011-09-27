from SimpleXMLRPCServer import SimpleXMLRPCServer
import glob
import os
import os.path as op
import random
import threading
import time
import gtk
import gobject
import numpy
from mayolmol.mlmusings import neighbors, mlio
from mayolmol.others import ubigraph, gtkpoc, othersoft

def default_class_to_color(clazz):
    COLORS = ["#ff0000", #Red
              "#ffff00", #Yellow
              "#00ff00", #Green
              "#0000ff"] #Blue
    return COLORS[int(clazz)]

class UbigraphHelper():
    def __init__(self, U=None, callback_port=None):
        self.U = UbigraphHelper.connect() if not U else U
        if callback_port:
            self.server_address = "http://127.0.0.1:" + str(callback_port) + "/" + 'vertex_callback'

    @staticmethod
    def connect(ubigraph_location=None, clear=True):
        if not ubigraph_location: os.system(othersoft.OtherSoft().ubigraph +' -quiet &')
        else: os.system(op.join(ubigraph_location, 'ubigraph_server' + ' -quiet &'))
        time.sleep(1)
        U = ubigraph.Ubigraph()
        if clear: U.clear()
        return U

    def populate(self, neighbors, y, class_to_color=None, clear=True):
        if clear: self.U.clear()
        U = self.U
        nodes = []
        if not class_to_color: class_to_color = lambda clazz: str(clazz)
        stylesVertices = [U.newVertexStyle(id=int(clazz) + 1,
                                           color=class_to_color(clazz),
                                           shape="sphere") for clazz in sorted(set(y))]
        if self.server_address:
            for style in stylesVertices:
                U.server.ubigraph.set_vertex_style_attribute(style.id,
                                                             "callback_left_doubleclick",
                                                             self.server_address)

        styleWrongEdge = U.newEdgeStyle(id=133, color="#ff0000", stroke="dashed")
        for nodeIndex in range(len(neighbors)):
            nodes.append(U.newVertex(nodeIndex, style=stylesVertices[int(y[nodeIndex])]))
        for nodeIndex in range(len(neighbors)):
            for nn in neighbors[nodeIndex]:
                U.newEdge(nodes[nodeIndex], nodes[int(nn)],
                          style=(styleWrongEdge if y[nodeIndex] != y[int(nn)] else None))

def chem_ubigraph(x, y, pics=glob.glob('/home/santi/Proyectos/bsc/data/filtering/dsstox/BCF/depictions/*.png')):
    iw = gtkpoc.ImageWindow(pics)
    def vertex_callback(v):
        gtk.threads_enter()
        iw.setPic(v)
        gtk.threads_leave()
        return 0
    port = random.randint(20739, 20999)
    U = UbigraphHelper(callback_port=port)
    U.populate(neighbors.nns(x), y, class_to_color=default_class_to_color)
    server = SimpleXMLRPCServer(("localhost", port))
    server.register_introspection_functions()
    server.register_function(vertex_callback, 'vertex_callback')
    #Serve
    print 'Serving for ubigraph double clicks...'
    serving = lambda: threading.Thread(target=server.serve_forever).start()
    gobject.idle_add(serving)  #Actually it is enough to run this out of the GTK event thread...
    #Bring in the GTK window
    gtkpoc.gtk_run()

def random_problem(num_points=800, dimensionality=30):
    x = numpy.random.normal(size=(num_points, dimensionality))
    y = [0] * (num_points / 2) + [1] * (num_points - (num_points / 2))
    return x, y

def dsstox_problem(name='Mutagenicity'):
    root = op.join(op.expanduser('~'), 'Proyectos', 'bsc', 'data', 'filtering', 'dsstox', name)
    x = numpy.loadtxt(op.join(root, name +'-ob-spectrophores.csv'), delimiter=',')
    with open(op.join(root, name +'-master.csv')) as master:
        master.next()
        y = [1 if float(line.split(',')[2]) > 1 else 0 for line in master]
        y = numpy.array(y)
    pics = glob.glob(op.join(root, 'depictions', '*.png'))
    return x, y, pics

def generic_problem(arfffile=op.join(op.expanduser('~'), 'Proyectos', 'bsc', 'data', 'filtering', 'mutagenicity', 'all', 'mutagenicity-all-union-prepared-cdk-constitutional.arff')):
    _, _, _, x, y = mlio.load_arff(arfffile)
    root, _ = op.split(arfffile)
    pics = glob.glob(op.join(root, 'depictions', '*.png'))
    return x, y, pics

def linear_gradient(num_colors, num_color, start=0, end=255):
    return (end - start) * num_color / num_colors

#x, y, pics = dsstox_problem()
x, y, pics = generic_problem()
chem_ubigraph(x, y, pics)