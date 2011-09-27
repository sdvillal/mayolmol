# -*- coding: utf-8 -*-
""" Preparation for the mutagenicity datasets """
import os
import os.path as op
import pybel
from mayolmol.descriptors.jcompoundmapper import JCompoundMapperCLIDriver
from mayolmol.scripts.dsstox_depict import depict
from mayolmol.scripts.dsstox_prep import create_saliviewer_input, create_master_table, save_mols, rename_mols_by_index
from mayolmol.scripts.dsstox_prop4da import prop4da
from mayolmol.scripts.dsstox_properties import cdkdescuiprops, spectrophores

def aid2sdf(sdf, csv, dest=None):
    """ Reads a pubchem bioassay results and merge it with the SDF file """
    #Read the known activities to a dictionary        
    activities = {}
    for activity in open(csv).readlines()[1:]:
        value = activity.split(',')[5]
        molid = activity.split(',')[2]
        activities[molid] = value    
    #Save the activity to each molecule    
    mols = list(pybel.readfile('sdf', sdf))
    for mol in mols:        
        activity = activities[mol.title]
        if activity == 'Active': actual_activity = '1'
        elif activity == 'Inactive': actual_activity = '0'
        else: actual_activity = 'Missing'
        mol.data['Activity'] = actual_activity
    if dest: 
        save_mols(mols, dest)        
    return mols
    
def merge(mols1, mols2):
    """ Merge two collections of molecules.
        It returns the union, the interesction and the ambiguous pairs
        (same molecule with different outcomes).
    """
    present_can_smiles = {}
    intersection = []
    union = []
    ambiguous = []
    for mol in mols1 + mols2:
        can = mol.write('can').split()[0]
        if not can in present_can_smiles:
            present_can_smiles[can] = mol
            union.append(mol)
        else:
            intersection.append(mol)
            present_mol = present_can_smiles[can]
            if mol.data['Activity'] != present_mol.data['Activity']:
                ambiguous+=(present_mol, mol)
    return union, intersection, ambiguous

def prepare_dataset(sdffile, dest=None, rename=True, conformations=False, overwrite=False):
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
    master_table = op.join(dest, name + '-prepared-master.csv')
    sali_table = op.join(dest, name + '-prepared-saliviewer.csv')

    if op.exists(dest_sdf) and not overwrite:
        print '%s is already there and not overwriting requested' % dest_sdf
    else:
        print 'Reading %s' % sdffile
        mols = list(pybel.readfile('sdf', sdffile))

        print '\tCreating dataset root: %s' % dest
        if not op.exists(dest):
            os.makedirs(dest)

        if rename:
            print '\tRenaming the compounds to keep track of the provenance'
            rename_mols_by_index(mols, name + '-')

        if conformations:
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

    root = op.join(op.expanduser('~'), 'Proyectos', 'bsc', 'data', 'filtering', 'mutagenicity', 'all')

    dest_sdf = op.join(root, 'mutagenicity-all-union-prepared.sdf')

    print 'Saving in several data analysis tools file formats'
    prop4da(dest_sdf)

    print 'Merging the datasets'

    ames_original = op.join(root, 'ames.sdf')
    bursi_original = op.join(root, 'bursi.sdf')
    dsstox_original = op.join(root, 'dsstox.sdf')

    print '\tReading the sdf files'
    mols_ames = list(pybel.readfile('sdf', ames_original))
    mols_bursi = list(pybel.readfile('sdf', bursi_original))
    mols_dsstox = list(pybel.readfile('sdf', dsstox_original))

    #The activity is always stored in the same field
    for mol in mols_bursi:
        activity = '1' if mol.data['Ames test categorisation'] == 'mutagen' else '0'
        mol.data['Activity'] = activity

    for mol in mols_dsstox:
        mol.data['Activity'] = mol.data['Tox']

    print '\tRenaming the compounds to keep track of the provenance'
    rename_mols_by_index(mols_ames, 'ames-')
    rename_mols_by_index(mols_bursi, 'bursi-')
    rename_mols_by_index(mols_dsstox, 'dsstox-')

#    aid1189csv = '1189aid.csv'
#    aid1189sdf = 'AID1189.sdf'
#    aid1194csv = '1194aid.csv'
#    aid1194sdf = 'AID1194.sdf'
#    aid1189mols = aid2sdf(aid1189sdf, aid1189csv, 'aid1189-prepared.sdf')
#    aid1194mols = aid2sdf(aid1194sdf, aid1194csv, 'aid1194-prepared.sdf')

    print '\tComputing the union of the datasets'
    union, intersection, ambiguous = merge(mols_ames, mols_bursi + mols_dsstox)
    save_mols(union, op.join(root, 'mutagenicity-all-union.sdf'))
    save_mols(intersection, op.join(root, 'mutagenicity-all-intersection.sdf'))
    save_mols(ambiguous, op.join(root, 'mutagenicity-all-ambiguous.sdf'))
    print '\t\tUnion size=%d, Intersection size=%d, Ambiguous size=%d'%(len(union), len(intersection), len(ambiguous))

    dest_sdf, _ = prepare_dataset(op.join(root, 'mutagenicity-all-union.sdf'), rename=False, conformations=True)

    #Depict the molecules
    depict(dest_sdf)

    #Molecular descriptors
    print 'Computing descriptors via CDKDescUI'
    cdkdescuiprops(dest_sdf, desc_types=('constitutional,'))
    print 'Computing spectrophores'
    spectrophores(dest_sdf)
    print 'Computing fingerprints via JCompoundMapper' #TODO: Extract-method this
    FINGERPRINTS = ('ECFP', 'CATS2D', 'PHAP3POINT2D', 'DFS', 'RAD2D')
    for fp in FINGERPRINTS:
        print fp
        output = op.join(root, 'mutagenicity-all-union-jcm-' +fp +'.arff')
        JCompoundMapperCLIDriver().fingerprint(dest_sdf, output, label='Activity', hash_space_size=2**10)
        #TODO: sparse to non-sparse
        #Use http://weka.sourceforge.net/doc.dev/weka/filters/unsupervised/instance/SparseToNonSparse.html
        #java -cp weka.jar weka.filters.unsupervised.instance.SparseToNonSparse -i sparse.arrf -o dense.arff -c last