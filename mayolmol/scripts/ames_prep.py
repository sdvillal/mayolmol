""" Preparation for the ames-mutagenicity dataset at http://doc.ml.tu-berlin.de/toxbenchmark/information_v2.html
    See also:
      - http://www.opentox.org/meet/opentox2011/abstracts/modeling-ames-mutagenicity-using-machine-learning-methods-2013-a-comparative-study
      - JMLR "How to explain individual classification decisions"
"""
import os
import os.path as op
import pybel
from mayolmol.descriptors.jcompoundmapper import JCompoundMapperCLIDriver
from mayolmol.scripts.dsstox_depict import depict
from mayolmol.scripts.dsstox_prep import create_saliviewer_input, create_master_table, save_mols, rename_mols_by_index
from mayolmol.scripts.dsstox_prop4da import prop4da
from mayolmol.scripts.dsstox_properties import cdkdescuiprops, spectrophores

def prepare_dataset(sdffile, dest=None, overwrite=False):
    """ This method bootstraps the analysis of Ames data.
       - Rename the compounds
       - Merge train/test
       - Generate 3D conformations
       - Save "master" and "saliviewer" tables
       - Redirects stdout/stderr to a "prepare.log" file
    """
    root, name = op.split(sdffile)
    name = op.splitext(name)[0]

    if not dest: dest = root

    dest_sdf = op.join(dest, name + '-prepared.sdf')
    master_table = op.join(dest, name + '-master.csv')
    sali_table = op.join(dest, name + '-saliviewer.csv')

    if op.exists(dest_sdf) and not overwrite:
        print '%s is already there and not overwriting requested' % dest_sdf
    else:
        print 'Reading %s' % sdffile
        mols = list(pybel.readfile('sdf', sdffile))

        print '\tCreating dataset root: %s' % dest
        if not op.exists(dest):
            os.makedirs(dest)

        print '\tRenaming the compounds to keep track of the provenance'
        rename_mols_by_index(mols, name + '-')

        print '\tGenerating conformations'
        for mol in mols:
            if not any(name in mol.title for name in ('train-3988', 'train-4205')):
                try:
                    print 'Conformation for %s' % mol.title
                    mol.make3D()
                except Exception:
                    print 'Error computing a 3D conformation for %s' % mol.title

        print '\tSaving compounds'
        save_mols(mols, dest_sdf)

        print '\tCreating \"master\" table: %s' % master_table
        create_master_table(dest_sdf, master_table, fields=['Activity'])

        print '\tCreating \"saliviewer\" table: %s' % sali_table
        create_saliviewer_input(master_table, sali_table)

    return dest_sdf, master_table

if __name__ == '__main__':
    DEFAULT_AMESV2_DIR = op.join(op.expanduser('~'), 'Proyectos', 'bsc', 'data', 'filtering', 'mutagenicity')
    root = DEFAULT_AMESV2_DIR
    dataset = op.join(root, 'tox_benchmark_N6512.sdf') #TODO: check if it exists, otherwise download
    dest_sdf, master_table = prepare_dataset(dataset)

    #Depict the molecules
    depict(dest_sdf)

    #Molecular descriptors
    print 'Computing descriptors via CDKDescUI'
    cdkdescuiprops(dataset)
    print 'Computing spectrophores'
    spectrophores(dataset)
    print 'Saving in several data analysis tools file formats'
    prop4da(dataset)
    print 'Computing fingerprints via JCompoundMapper' #TODO: Extract-method this
    FINGERPRINTS = ('ECFP', 'CATS2D')
    for fp in FINGERPRINTS:
        print fp
        output = op.join(root, 'tox_benchmark_N6512-jcm-' +fp +'.arff')
        JCompoundMapperCLIDriver().fingerprint(dataset, output, label='Activity')