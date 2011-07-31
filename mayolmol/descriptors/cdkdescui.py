"""
Driver for using the CDKDescUI in batch mode.

java -jar CDKDescUI.jar -b -t constitutional
ERROR: Must specify a single input file
usage: cdkdescui [OPTIONS] inputfile

 -a    Add explicit H's
 -b    Batch mode
 -f    Fingerprint type: estate, extended, graph, standard, pubchem,
       substructure
 -h    Help
 -o    Output file
 -s    A descriptor selection file. Overrides the descriptor type option
 -t    Descriptor type: all, topological, geometric, constitutional,
       electronic, hybrid
 -v    Verbose output

CDKDescUI v1.3.2 Rajarshi Guha <rajarshi.guha@gmail.com>
"""


class CDKDescUIDriver():
    def __init__(self,
                 java_command = 'java',
                 cdkdeskuijar = '/home/santi/cdkdescui/CDKDescUI.jar'):
        self.command = java_command + ' ' +cdkdeskuijar

    def run(self, input, output, descs='constitutional', addH=False):
        pass

