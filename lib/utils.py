import json
import sys
import hashlib


def generation_nom():
    from random import randint
    return "%04X-%04X-%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000), randint(0, 0x10000), randint(0, 0x10000))


"""
===============================================================================
Pour test
===============================================================================
"""

def bytes_dict(**dico): # I8
    return json.dumps(dico).encode('utf-8')


def bytes_list(*lst): # I8
    return json.dumps(lst).encode('utf-8')

def dict_bytes(dico: bytes): # I8
    return eval(dico.decode())


def find_root():
    from os import getcwd
    from os import path
    if path.split(getcwd())[1] in ['lib', 'tx', 'etc', 'cache', 'cmds', 'outils', 'services', 'tests']:
        return path.split(getcwd())[0]
    else:
        return getcwd()


def get_name():
    import socket
    return socket.gethostname()


def get_ip(x=None):
    import socket
    if x:
        return socket.gethostbyname(x)
    else:
        return socket.gethostbyname(get_name())


def tprint(msg):
    """like print, but won't get newlines confused with multiple threads"""
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


def lst2key(lst: list) -> str:
    return hashlib.md5(str(lst).encode()).hexdigest()



def main():
    print(generation_nom())


if __name__ == "__main__": main()