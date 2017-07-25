import os, os.path
import conf

def dict_locate(tag):
    filename = conf.dict_conf.get(tag)
    if filename is None:
        return None

    return os.path.join(os.getcwd(), conf.dict_path, filename)

def dict_locate():
    dictfiles = [f for f in os.listdir(conf.dict_path) if f.endswith('.txt')]


