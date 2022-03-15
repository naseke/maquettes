import json


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


def main():
    print(generation_nom())


if __name__ == "__main__": main()