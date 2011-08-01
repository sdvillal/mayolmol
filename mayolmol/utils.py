""" Functions jumble """
import os.path as op
import os
import tarfile

def ensure_dir(dir):
    if not op.exists(dir):
        os.makedirs(dir)

def extract(tar_url, dest='.'):
    tar = tarfile.open(tar_url)
    for item in tar:
        tar.extract(item, dest)
