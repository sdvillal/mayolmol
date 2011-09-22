#Author: Santi. Slightly modified by Flo
from __future__ import with_statement
import subprocess
from mayolmol.others import othersoft

class CDKDescUIDriver():
    """
    Driver for using the CDKDescUI in batch mode. Here is the help of the command:

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
    def __init__(self,
                 java_command='java',
                 cdkdeskuijar=None):
        if not cdkdeskuijar: cdkdeskuijar = othersoft.OtherSoft().cdkdescui
        self.command = java_command + ' -jar ' + cdkdeskuijar

    def compute_type(self, input, output, desc_type='constitutional', addH=False):
        addH = ' -a' if addH else ''
        command = self.command + addH + ' -b -t ' + desc_type + ' -o ' + output + ' ' + input
        with open(output + '.err', 'w') as stderr:
            subprocess.call(command, shell=True, stdout=stderr, stderr=stderr)

    def compute_fingerprint(self, input, output, fingerprint='constitutional', addH=False):
        addH = ' -a' if addH else ''
        command = self.command + addH + ' -b -f ' + fingerprint + ' -o ' + output + ' ' + input
        with open(output + '.err', 'w') as stderr:
            subprocess.call(command, shell=True, stdout=stderr, stderr=stderr)

    def compute_selection(self, input, output, selection, addH=False):
        addH = ' -a' if addH else ''
        command = self.command + addH + ' -b -s ' + selection + ' -o ' + output + ' ' + input
        with open(output + '.err', 'w') as stderr:
            subprocess.call(command, shell=True, stdout=stderr, stderr=stderr)
