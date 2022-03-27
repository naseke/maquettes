#desc#
#desc##########################################################################
#desc# Class Params
#desc##########################################################################
#desc# Description : Récupère les paramaetres du fichier param.ini
#desc##########################################################################
#desc# V0.1		# N.SALLARES # init
#desc##########################################################################
#desc#

from lib.Singleton import SingletonMeta
from lib.utils import find_root
from os.path import join


class parametres:

	__VERSION = '0.01'

	@classmethod
	def get_VERSION(self):
		return self.__VERSION


class Params(metaclass=SingletonMeta):

	PARAMS = {}
		
	def __init__(self):
		self.__FIC_PARAM = join(find_root(), 'etc', 'param.ini') #a la windows :p
		self.PARAMS = self.__get_parametres(self.__FIC_PARAM)
	#findef
	
	def __get_parametres(self,fic_param):
		fic = open(fic_param, 'r')
		
		#recupération des lines 
		cont = fic.readlines()
		
		#nettoyage des lignes de commentaires, des lignes vierges, des \n et des blancs
		tmp = [elem.strip('\n').strip().replace("= ", "=").replace(" =", "=").replace(" = ", "=").split('=') for elem in cont if elem[:1] != '#' and elem[:1] != '\n']
		
		#il manque les commentaires au meme niveau dans la ligne
			
		# transformation en dict
		
		return dict(tmp)
	#findef
	
	def __str__(self):
		return str(self.PARAMS)
	#findef
	
#finclass


