# -*- coding: utf-8 -*-
""" Downlading, installing and management of all the non-python required apps. """
import os
import os.path as op
import urllib
from mayolmol.utils import ensure_dir, extract

class OtherSoft():

    CDKDESCUI_JAR_URL = 'http://rguha.net/code/java/CDKDescUI.jar'
    SALIVIEWER_JAR_URL = 'http://sali.rguha.net/sali.jar'
    UBIGRAPH_UBUNTU_URL = 'http://ubietylab.net/files/alpha-0.2.4/UbiGraph-alpha-0.2.4-Linux64-Ubuntu-8.04.tgz'
    JCOMPOUNDMAPPER_JAR_URL = 'http://dfn.dl.sourceforge.net/project/jcompoundmapper/jCMapperCLI.jar'
    WEKA_JAR_URL = 'http://heanet.dl.sourceforge.net/project/weka/weka-3-7/3.7.4/weka-3-7-4.zip'

    @staticmethod
    def install_ubigraph(root):
        print 'Installing ubigraph'
        root = op.join(root, 'ubigraph')
        if not op.exists(root):
            os.makedirs(root)
        downloaded, _ = urllib.urlretrieve(OtherSoft.UBIGRAPH_UBUNTU_URL,
                                           op.join(root, 'UbiGraph-alpha-0.2.4-Linux64-Ubuntu-8.04.tgz'))
        extract(downloaded, root)
        os.remove(downloaded)

    @staticmethod
    def install_weka(root):
        print 'Installing weka'
        root = op.join(root, 'weka')
        if not op.exists(root):
            os.makedirs(root)
        downloaded, _ = urllib.urlretrieve(OtherSoft.WEKA_JAR_URL,
                                           op.join(root, 'weka-3.7.4.zip'))
        from zipfile import ZipFile
        ZipFile(downloaded).extractall(path=root)
        os.remove(downloaded)

    @staticmethod
    def install_file(url, dest):
        if not op.exists(dest):
            ensure_dir(op.split(dest)[0])
            urllib.urlretrieve(url, dest)

    def __init__(self, root=None):
        if not root:
            root = op.join(op.split(op.realpath(__file__))[0], '3rdparty')
        self.root = root
        self.ubigraph = op.join(self.root, 'ubigraph',
                                'UbiGraph-alpha-0.2.4-Linux64-Ubuntu-8.04',
                                'bin', 'ubigraph_server')
        if not op.exists(self.ubigraph): OtherSoft.install_ubigraph(self.root)

        self.cdkdescui = op.join(root, 'cdkdescui', 'CDKDescUI.jar')
        OtherSoft.install_file(OtherSoft.CDKDESCUI_JAR_URL, self.cdkdescui)

        self.saliviewer = op.join(root, 'saliviewer', 'saliviewer.jar')
        OtherSoft.install_file(OtherSoft.SALIVIEWER_JAR_URL, self.saliviewer)

        self.jcompoundmapper = op.join(root, 'jcompoundmapper', 'jcompoundmapper.jar')
        OtherSoft.install_file(OtherSoft.JCOMPOUNDMAPPER_JAR_URL, self.jcompoundmapper)

        self.weka = op.join(self.root, 'weka', 'weka-3-7-4', 'weka.jar')
        if not op.exists(self.weka): OtherSoft.install_weka(self.root)

OtherSoft()