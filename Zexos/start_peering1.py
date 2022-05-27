from lib import parametres

p = parametres.Params()

print(p)
print(p.PARAMS['other_bus1'])
print(eval(p.PARAMS['other_bus1']))
# print(p.PARAMS['other_bus1'].strip('[]').split(','))
