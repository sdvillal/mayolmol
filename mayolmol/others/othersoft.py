# -*- coding: utf-8 -*-
""" Downlading, installing and management of all the non-python required apps. """
import os
import os.path as op
import urllib
import tarfile

def ensure_dir(dir):
    if not op.exists(dir):
        os.makedirs(dir)

def extract(tar_url, extract_path='.'):
    tar = tarfile.open(tar_url)
    for item in tar:
        tar.extract(item, extract_path)
        if item.name.find(".tgz") != -1 or item.name.find(".tar") != -1:
            extract(item.name, "./" + item.name[:item.name.rfind('/')])

class OtherSoft():

    CDKDESCUI_JAR_URL = 'http://rguha.net/code/java/CDKDescUI.jar'
    SALIVIEWER_JAR_URL = 'http://sali.rguha.net/sali.jar'
    UBIGRAPH_UBUNTU_URL = 'http://ubietylab.net/files/alpha-0.2.4/UbiGraph-alpha-0.2.4-Linux64-Ubuntu-8.04.tgz'

    @staticmethod
    def install_ubigraph(root):
        root = op.join(root, 'ubigraph')
        if not op.exists(root):
            os.makedirs(root)
        downloaded, _ = urllib.urlretrieve(OtherSoft.UBIGRAPH_UBUNTU_URL,
                                           op.join(root, 'UbiGraph-alpha-0.2.4-Linux64-Ubuntu-8.04.tgz'))
        extract(downloaded, root)
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

OtherSoft()