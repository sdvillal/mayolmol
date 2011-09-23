# -*- coding: utf-8 -*-
""" Generate different descriptors for the user's dataset. Directly inspired from Santi's dsstox_properties.py script. """
import os
import os.path as op
import pybel
import numpy
import sys
from mayolmol.descriptors import ob as spec
import mayolmol.descriptors.cdkdescui as cdkdescui

def spectrophores(dataset, overwrite=True):
    """ Compute the spectrophores for a dataset """
    try:
        print '\tSpectrophores'
        specs = spec.spectrophores(pybel.readfile('sdf', dataset))
        dataset_root, dataset_name = op.split(dataset)
        dataset_name = op.splitext(dataset_name)[0]
        #numpy.savetxt(op.join(dataset_root, dataset_name + '-ob-spectrophores.csv'),
                      #specs, fmt='%s %.6f', delimiter=',')
        destfile = op.join(dataset_root, dataset_name + '-ob-spectrophores.csv')
        if op.exists(destfile) and overwrite==False:
            print '%s is already there and not overwriting requested' % destfile
            return
        else:
            if op.exists(destfile) and overwrite==True:
                print '%s is already there but overwriting requested' % destfile
                os.remove(destfile)
            f= open(destfile, 'a')    
            for molecule in specs:
                f.write(molecule[0])
                f.write(",")
                for i in range(1,49):
                    f.write(str(molecule[i]))
                    f.write(",")
                f.write("\n")
            f.close()
            print '\tSpectrophores computed succesfully'
    except Exception, e:
        print 'Damn, there has been a problem computing the spectrophores...'
        print 'Research into this...'
        print e.message

if __name__ == '__main__':
    #CDKDescUI based properties
    #CDK_DEFAULT_TYPES = ['constitutional', 'geometric']
    #CDK_DEFAULT_DESCRIPTORS = op.join(op.split(__file__)[0], "../data/GuhaDescriptors")
    #CDK_DEFAULT_FINGERPRINTS = ['maccs', 'estate', 'extended']
    dataset = sys.argv[1]
    #print 'Computing properties for %s' % dataset
    #cdkdescui.CDKDescUIDriver().compute_selection(dataset,
                                                     #op.splitext(dataset)[0] + '-cdk' + '.csv',
                                                     #CDK_DEFAULT_DESCRIPTORS,
                                                     #addH=True)
    #for fingerprint in CDK_DEFAULT_FINGERPRINTS:
        #print '\t' + fingerprint
        #cdkdescui.CDKDescUIDriver('java', "/mmb/pluto/fmontanari/Build/CDKDescUI.jar").compute_fingerprint(dataset,
                                                            #op.splitext(dataset)[0] + '-cdk-' + fingerprint + '.csv',
                                                            #fingerprint=fingerprint,
                                                            #addH=True)
    spectrophores(dataset)
