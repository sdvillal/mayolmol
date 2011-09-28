# -*- coding: utf-8 -*-
""" Preparation for the mutagenicity datasets """
import os
import os.path as op
import pybel
from mayolmol.descriptors.jcompoundmapper import JCompoundMapperCLIDriver
from mayolmol.others.wekacli import WekaCLIDriver
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

def duplicates_by_format(mols, format='inchi'):
    #TODO: a function "duplicates taking" a lambda to extract the key
    merged = {}
    for mol in mols:
        id = mol.write(format)
        if not id in merged:
            merged[id] = [mol]
        else:
            merged[id].append(mol)
    return merged

def duplicates_by_field(mols, field='CAS_NO'):
    #TODO: a function "duplicates taking" a lambda to extract the key
    merged = {}
    for mol in mols:
        id = mol.data[field]
        if not id in merged:
            merged[id] = [mol]
        else:
            merged[id].append(mol)
    return merged

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
                if not any(name in mol.title for name in ('train-3988', 'train-4205', 'dsstox-4205', 'dsstox-4206')):
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

def jcm_fingerprint(sdf, fingerprints, label='Activity', hash_space_size=2**10, as_dense_too=True):
    #TODO: use multiprocessing
    for fp in fingerprints:
        print '\t' + fp
        output = op.splitext(sdf)[0] + '-jcm-' + fp + '.arff'
        JCompoundMapperCLIDriver().fingerprint(sdf, output, fingerprint=fp, label=label,
                                               hash_space_size=hash_space_size)
        if as_dense_too:
            WekaCLIDriver().sparse2dense(output)

if __name__ == '__main__':
    root = op.join(op.expanduser('~'), 'Proyectos', 'bsc', 'data', 'filtering', 'mutagenicity', 'all')

    print 'Merging the datasets'

    ames_original = op.join(root, 'ames.sdf')
    bursi_original = op.join(root, 'bursi.sdf')
    dsstox_original = op.join(root, 'dsstox.sdf')

    print '\tReading the sdf files'
    mols_ames = list(pybel.readfile('sdf', ames_original))
    mols_bursi = list(pybel.readfile('sdf', bursi_original))
    mols_dsstox = list(pybel.readfile('sdf', dsstox_original))

    print 'Num molecules ames=%d, bursi=%d, dsstox=%d' % (len(mols_ames), len(mols_bursi), len(mols_dsstox))

    #The activity is always stored in the same field
    for mol in mols_bursi:
        activity = '1' if mol.data['Ames test categorisation'] == 'mutagen' else '0'
        mol.data['Activity'] = activity
        mol.data['CAS_NO'] = mol.title

    for mol in mols_dsstox:
        mol.data['Activity'] = mol.data['Tox']
        mol.data['CAS_NO'] = mol.data['CAS']

    print '\tRenaming the compounds to keep track of the provenance'
    rename_mols_by_index(mols_ames, 'ames-')
    rename_mols_by_index(mols_bursi, 'bursi-')
    rename_mols_by_index(mols_dsstox, 'dsstox-')

    print '\tComputing and analyzing the union of the datasets'
    cas_dupes = duplicates_by_field(mols_ames + mols_bursi + mols_dsstox)
    #inchi_dupes = duplicates_by_format(mols_ames + mols_bursi + mols_dsstox,)
    #can_dupes = duplicates_by_format(mols_ames + mols_bursi + mols_dsstox, 'can')
    union = sorted([dupe[0] for dupe in cas_dupes.values()], key=lambda mol: mol.title)
    save_mols(union, op.join(root, 'mutagenicity-all-cas-union.sdf'))
    print '\t\tUnion size=%d' % len(union)

    dest_sdf = op.join(root, 'mutagenicity-all-cas-union-prepared.sdf')
    prepare_dataset(op.join(root, 'mutagenicity-all-cas-union.sdf'), rename=False, conformations=True)

    #Depict the molecules
    depict(dest_sdf)

    #Molecular descriptors
    print 'Computing descriptors via CDKDescUI'
    cdkdescuiprops(dest_sdf, desc_types=('constitutional',))
    print 'Computing spectrophores'
    spectrophores(dest_sdf)
    print 'Saving in several data analysis tools file formats'
    prop4da(dest_sdf)
    print 'Computing fingerprints via JCompoundMapper' #TODO: Extract-method this
    jcm_fingerprint(dest_sdf, ('ECFP', 'ECFPVariant', 'PHAP3POINT2D', 'SHED', 'DFS', 'RAD2D'))