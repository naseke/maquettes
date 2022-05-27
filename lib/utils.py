import json
import sys
import hashlib
from random import randint
import signal


def generation_nom_node() -> str:
    """
    Créer le nom du node de cette manière 3EDE-A79A-744D-DDED

    :return: le nom du node
    """
    return "%04X-%04X-%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000), randint(0, 0x10000), randint(0, 0x10000))


def generation_code(taille: int=4, nb: int=4) -> str:
    """
    Créer des chaînes de caractères du genre 3EDE-A79A-744D-DDED

    :param taille: Taille du bloc
    :param nb: Nombre du bloc
    :return: la chaîne de caractère

    todo: fonction à decliner par besoin car 3-4 plus lent que generation_nom_node
    """

    # return "%04X-%04X-%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000), randint(0, 0x10000), randint(0, 0x10000))
    # return f"""{'-'.join([f"{eval("randint(0, 0x1{0*4})"):04X}" for _ in range(4)])}"""
    return '-'.join([f"""{eval(f"randint(0, 0x1{'0'*taille})"):0{taille}X}""" for _ in range(nb)])


def bytes_dict(dico: dict) -> bytes:  # I8
    """
    transforme un dictionnaire en octets

    :param dico: un dict
    :return: un dict en octets
    """
    return json.dumps(dico).encode('utf-8')


def dict2bytes(dico: dict) -> bytes:  # I8
    """
    transforme un dictionnaire en octets

    :param dico: un dict
    :return: un dict en octets
    """
    return json.dumps(dico).encode('utf-8')


def bytes_list(lst: list) -> bytes:  # I8
    """
    transforme une liste en octets

    :param lst: une liste
    :return: une liste en octets
    """
    return json.dumps(lst).encode('utf-8')


def list2bytes(lst: list) -> bytes:  # I8
    """
    transforme une liste en octets

    :param lst: une liste
    :return: une liste en octets
    """
    return json.dumps(lst).encode('utf-8')


def dict_bytes(dico: bytes) -> dict: # I8
    """
    transforme un byte en dico

    :param dico: un dict
    :return: un dict en byte
    """
    return bytes2dict(dico)


def bytes2dict(dico: bytes) -> dict: # I8
    """
    transforme un byte en dico

    :param dico: un dict
    :return: un dict en byte
    """
    return json.loads(dico)

def bytes2list(lst: bytes) -> list: # I8
    """
    transforme un byte en list

    :param lst: un list en byte
    :return: bytes en list
    """
    return json.loads(lst)


def find_root() -> str:
    """
    Retrouve de façon basic le répertoire de base de l'application à partir d'une execution faite dans un répertoire enfant

    :return: le répertoire de base de l'application
    """
    from os import getcwd
    from os import path
    if path.split(getcwd())[1] in ['lib', 'tx', 'etc', 'cache', 'cmds', 'outils', 'services', 'tests']:
        return path.split(getcwd())[0]
    else:
        return getcwd()


def get_name() -> str:
    """
    Retourne le nom de la machine

    :return: le nom de la machine
    """
    import socket
    return socket.gethostname()


def get_ip(x: str = None) -> str:
    """
    Retourne l'adresse ip de la machine

    :param x: le nom de la machine
    :return: l'adresse ip de la machine
    """
    import socket
    if x:
        return socket.gethostbyname(x)
    else:
        return socket.gethostbyname(get_name())


def tprint(msg: str) -> None:
    """
    like print, but won't get newlines confused with multiple threads

    :param msg: chaine de caractère
    :return: None
    """
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


def lst2key(lst: list) -> str:
    """
    transformation d'une list en clé de hashage

    :param lst: liste à hasher
    :return: clé de hashage
    """
    return hashlib.md5(str(lst).encode()).hexdigest()


def init_worker() -> None:
    """
    Initialise les signaux pour les processus générés par le multiprocessing.
    à utiliser comme pointeur de fonction pas comme la fonction en elle-même
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)


"""
===============================================================================
Pour test
===============================================================================
"""

def main():
    print(generation_code())
    print(get_name())
    print(get_ip())
    print(lst2key(['toto', 'tutu']))


if __name__ == "__main__": main()