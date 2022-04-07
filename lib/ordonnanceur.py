import asyncio
from datetime import datetime,timedelta
from lib import couleurs, utils


class ordonnanceur:
    __VERSION = '0.01'

    @classmethod
    def get_VERSION(self):
        return self.__VERSION


class Ordonnanceur:

    def __init__(self, debug=False):
        self.tasks = {}
        self.index = {}
        self._debug = debug
        self.__continu = False

    def add_task(self, tache, recurent, *params, **quand):
        # contrôle de redondance surtout avec le risque de deux appelles consécutifs avec le même hash...
        # /!\ result ne contient qu'une liste de hash
        if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Ajout")
        result = [f for f in self.tasks if self.tasks[f][0] == tache and self.tasks[f][1] == recurent and self.tasks[f][3] == params and self.tasks[f][2] == quand]
        if self._debug: couleurs.AffichageColor().msg_DEBUG(f"result: {str(result)}")
        if not result:
            couleurs.AffichageColor().msg_INFO(f"ajout de {tache} pour execution dans {quand}")
            t = datetime.now() + timedelta(**quand)
            htache = utils.lst2key([tache, recurent, quand, params, t])
            self.tasks[htache] = [tache, recurent, quand, params, t]
            if t in self.index.keys():
                self.index[t].append(htache)
            else:
                self.index[t] = [htache]
        else:
            if recurent:
                couleurs.AffichageColor().msg_WARNING(f'tâche {tache} avec ces paramètres {params} toutes les {quand} existe déjà')
            else:
                couleurs.AffichageColor().msg_WARNING(f'tâche {tache} avec ces paramètres {params} dans les {quand} existe déjà')
        if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Tâches : {str(self.tasks)}")
        if self._debug: couleurs.AffichageColor().msg_DEBUG(f"Index : {str(self.index)}")

    def del_task(self, tache, recurent, *params, **quand):
        # /!\ result ne contient qu'une liste de hash
        result = [f for f in self.tasks if self.tasks[f][0] == tache and self.tasks[f][1] == recurent and self.tasks[f][3] == params and self.tasks[f][2] == quand]
        if self._debug: couleurs.AffichageColor().msg_DEBUG(f"result: {str(result)}")
        if result:
            couleurs.AffichageColor().msg_INFO(f"suppression de {tache} avec un interval de {quand}")
            self._del_task(self.tasks[result[0]][4], result[0])
        else:
            if recurent:
                couleurs.AffichageColor().msg_WARNING(f"tâche {tache} avec ces paramètres {params} toutes les {quand} n'existe pas")
            else:
                couleurs.AffichageColor().msg_WARNING(f"tâche {tache} avec ces paramètres {params} dans les {quand} n'existe pas")

    def _del_task(self, tache_index, htache):
        try:
            del self.tasks[htache]
            if len(self.index[tache_index]) > 1:
                del self.index[tache_index][self.index[tache_index].index(htache)]
            else:
                del self.index[tache_index]

        except KeyError:
            return -1
        return 0

    def stop(self):
        if self.__continu:
            couleurs.AffichageColor().msg_WARNING("Arret de l'ordonnanceur")
            self.__continu = False

    def start(self):
        from time import sleep

        self.__continu = True
        couleurs.AffichageColor().msg_INFO("démarrage de l'ordonnanceur")
        while self.__continu:
            sleep(0.001)
            lst_exec = [elem for elem in list(self.index.keys()) if elem < datetime.now()]
            if len(lst_exec) > 0:
                for elem in lst_exec:
                    htache = self.index[elem][0]
                    tache = self.tasks[htache][0]
                    recurent = self.tasks[htache][1]
                    quand = self.tasks[htache][2]
                    params = self.tasks[htache][3]
                    couleurs.AffichageColor().msg_OK(f"execution de {tache} avec un interval de {quand}")
                    getattr(self, tache)(*params)
                    if not self._del_task(elem, htache):
                        if recurent:
                            self.add_task(tache, recurent, *params, **quand)

    def execute(self, tache):
        return tache in self.tasks.keys()


class OrdoSvr(Ordonnanceur):

    def send_msg(self, obj):
        obj.msg_send_like_exo()


class Test(Ordonnanceur):

    def test1(self):
        print('test1')


    def test2(self,*args):
        print(f'test2: {args[0]} | {args[1]}')

def main():
    import threading
    import time

    ordo = Test()
    t = threading.Thread(target=ordo.start, daemon=True)
    t.start()
    ordo.add_task('test2', False, 'test', '10s', seconds=10)
    #ordo.add_task('test1', True, seconds=2)
    ordo.add_task('test2', True, 'fun', 'super', seconds=3)
    ordo.add_task('test2', True, 'fun', 'super', seconds=3)
    time.sleep(15)
    ordo.del_task('test2', True, 'fun', 'super', seconds=3)
    time.sleep(5)
    ordo.stop()


if __name__ == "__main__": main()
