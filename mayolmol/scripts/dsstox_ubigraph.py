import os
import os.path as op
import random
import time
from PyQt4.QtGui import QDialog, QGridLayout, QApplication
from PyQt4.QtSvg import QSvgWidget
import sys
import numpy
from mayolmol.mlmusings import neighbors
from mayolmol.others import ubigraph
from SimpleXMLRPCServer import SimpleXMLRPCServer

class CompoundPalette(QDialog):
    """ Little window for showing images.
        Thanks to Flo.
        TODO: look into QSvgWidget (does not seem to be very good at rendering OBs SVG)
    """

    def __init__(self, pics=None, parent=None):
        super(QDialog, self).__init__(parent)
        if not pics: pics = []
        self.setWindowTitle("Image Viewer")
        self.setLayout(QGridLayout(self))
        self.resize(300, 300)
        self.pics = [QSvgWidget(pic) for pic in pics]
        self.defaultWidget = QSvgWidget(
            '/home/santi/Proyectos/bsc/data/filtering/dsstox/BCF/depictions/BCF-test-001.svg')
        self.defaultWidget.resize(200, 200)
        self.display()

    def display(self, picNum=None):
        if not picNum or picNum not in range(len(self.pics)):
            self.layout().addWidget(self.defaultWidget, 0, 0)
        else:
            self.layout().addWidget(self.pics[picNum], 0, 0)
        self.repaint()

    def show_standalone(self):
        app = QApplication(sys.argv)
        dlg = CompoundPalette()
        dlg.show()
        app.exec_()


class UbigraphHelper():

    def __init__(self, U=None, vertex_callback=None, callback_port=None):
        self.U = UbigraphHelper.connect() if not U else U
        self.vertex_callback = vertex_callback
        self.server_address = None
        self.server = None
        # Create callback server
        if vertex_callback and callback_port:
            self.server = SimpleXMLRPCServer(("localhost", callback_port))
            self.server.register_introspection_functions()
            self.server.register_function(vertex_callback)
            self.server_address = "http://127.0.0.1:" + str(callback_port) + "/" +vertex_callback.__name__

    @staticmethod
    def connect(ubigraph_location=None, clear=True):
        if not ubigraph_location: os.system('ubigraph_server -quiet &')
        else: os.system(op.join(ubigraph_location, 'ubigraph_server' + ' -quiet'))
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

    def serve_forever(self):
        if self.server: self.server.serve_forever()

def vertex_callback2(v):
    try:
        print v
    except Exception:
        return -1
    return 0

x = numpy.random.normal(size=(30, 30))
y = [0] * 15 + [1] * 15
U = UbigraphHelper(vertex_callback=vertex_callback2, callback_port=random.randint(20739,20999))
U.populate(neighbors.nns(x), y)

U.serve_forever()