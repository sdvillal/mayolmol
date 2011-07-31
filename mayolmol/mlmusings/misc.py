# -*- coding: utf-8 -*-
import os
import shutil
import getpass
import fnmatch

def curry(fn, *cargs, **ckwargs):
    def call_fn(*fargs, **fkwargs):
        d = ckwargs.copy()
        d.update(fkwargs)
        return fn(*(cargs + fargs), **d)
    return call_fn

def ensure_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def recursive_list(root, pattern):
    matches = []
    for root, dirnames, filenames in os.walk(root):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))
    return matches

def immediate_subdirectories(dir):
    return [os.path.join(dir, name) for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name))]

def rm_tree(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)

def username():
    getpass.getuser()

def file_to_str(src):
    if isinstance(src, str):
        return src
    elif isinstance(src, file):
        return src.name
    raise Exception('Not a string nor a file')