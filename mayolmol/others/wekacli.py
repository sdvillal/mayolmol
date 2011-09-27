import subprocess
import os.path as op
from mayolmol.others import othersoft

class WekaCLIDriver():
    """ Some methods to access weka via command line using python. """

    def __init__(self,
                 java_command='java',
                 wekajar=None):
        if not wekajar: wekajar = othersoft.OtherSoft().weka
        self.command = java_command + ' -cp ' + wekajar

    def sparse2dense(self, sparse, dense=None):
        """ Save an sparse ARFF file as dense. """

        if not dense: dense = op.splitext(sparse) +'-dense.arff'

        filter_class = ' weka.filters.unsupervised.instance.SparseToNonSparse'

        command = self.command +\
                  filter_class +\
                  ' -i ' +sparse +\
                  ' -o ' +dense

        subprocess.call(command, shell=True)