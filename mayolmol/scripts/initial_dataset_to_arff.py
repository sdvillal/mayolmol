# -*- coding: utf-8 -*-
import sys
import os.path as op
import mayolmol.scripts.prepare_dataset as prep
import pybel
import mayolmol.scripts.compute_properties as prop
import mayolmol.descriptors.cdkdescui as cdkdescui
import mayolmol.scripts.dsstox_prop4da as arff

if __name__ == "__main__":
    
    if len(sys.argv) == 3:
        dataset = sys.argv[1]
        if op.exists(dataset):
            directory = op.dirname(dataset)
            file = op.basename(dataset)
            to_predict = sys.argv[2]
            prepared_data, master_file = prep.prepare_user_dataset(directory, file, to_predict)
            CDK_DEFAULT_DESCRIPTORS = op.join(op.split(__file__)[0], "../data/GuhaDescriptors")
            CDK_DEFAULT_FINGERPRINTS = ['maccs', 'estate', 'extended']
            print 'Computing properties for %s' % prepared_data
            cdkdescui.CDKDescUIDriver().compute_selection(prepared_data,
                                                     op.splitext(prepared_data)[0] + '-cdk' + '.csv',
                                                     CDK_DEFAULT_DESCRIPTORS,
                                                     addH=True)
            descriptors_file = op.splitext(prepared_data)[0] + '-cdk' + '.csv'
            fingerprint_files = []
            for fingerprint in CDK_DEFAULT_FINGERPRINTS:
                print '\t' + fingerprint
                cdkdescui.CDKDescUIDriver('java', "/mmb/pluto/fmontanari/Build/CDKDescUI.jar").compute_fingerprint(prepared_data,
                                                            op.splitext(prepared_data)[0] + '-cdk-' + fingerprint + '.csv',
                                                            fingerprint=fingerprint,
                                                            addH=True)
                fingerprint_files.append((fingerprint, op.splitext(prepared_data)[0] + '-cdk-' + fingerprint + '.csv'))
            spectrophores_file = prop.spectrophores(dataset)
            print "Converting to .arff format the spectrophore file %s."%spectrophores_file
            arff.spectrophores_to_arff(directory, op.basename(master_file), op.basename(spectrophores_file), to_predict)
            print "Converting to .arff format the intrinsic descriptors file %s."%descriptors_file
            arff.cdk_desc_to_arff(directory, op.basename(master_file), op.basename(descriptors_file), to_predict)
            for file in fingerprint_files:
                print "Converting to .arff format the fingerprint file %s."%file[1]
                arff.cdk_fpt_to_arff(directory, op.basename(master_file), op.basename(file[1]), to_predict, file[0])

        else:
            print "There is no such file %s."%dataset
            sys.exit()
    else:
        print "Too many or too little arguments. Please remember:\n - the first argument is the absolute path to the dataset file\n - the second argument is the name of the property you want to predict, as written in the corresponding .sdf section"
        sys.exit()
        
