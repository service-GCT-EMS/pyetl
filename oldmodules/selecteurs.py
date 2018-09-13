# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions s de selections : determine si une regle est eligible ou pas
"""
import re
from .fonctions.outils import compilefonc


class Selecteur(object):
    ''' outil de selection permettend de savoir si une regle est eligible
        tous les selecteurs partagent un espace de stockage pemettant de gerer les
        listes dynamiques (les listes statique sont gerees par les instances):
    '''
    dynlists = dict()
    dynkeys = dict()

    @classmethod
    def set_list(cls, clef, liste, dynvals):
        '''initialise les listes dynamiques'''
        cls.dynlists[clef] = liste
        cls.dynkeys[clef] = dynvals

    @staticmethod
    def true(_):
        '''toujours vrai'''
        return True
    @staticmethod
    def false(_):
        '''toujours faux'''
        return False

    def __init__(self, attribut, mode_select, valeurs, regle, negation):
        ''' determine si une regle s applique a l objet '''
        self.attribut = attribut
        self.valeurs = valeurs
        self.precedent = None

        self.stock_param = regle.stock_param
        self.regle = regle
        self.schemaqueries = dict()
        self.complement = None
        self.cnum = None
#        self.s3D = 'False'
        self.val_tri = None
        debug = regle.debug
#        print("selecteur:", mode_select)
        if ',' in mode_select:
            msel = mode_select.split(',')
            mode_select = msel[0]
            self.complement = msel[1]
            try:
                self.cnum = int(self.complement)
            except ValueError:
                try:
                    self.cnum = float(self.complement)
                except ValueError:
                    self.cnum = None

        if mode_select == "in_s":
            if isinstance(self.attribut, list):
                self.select = self.vals_in_s
            else:
                self.select = self.classe_in_s

        elif mode_select == 'id_in_s':
            self.select = self.id_regex
        elif mode_select == 'in_a':
            self.select = self.classe_in_a
        elif mode_select == 'in_d':



            self.select = self.classe_in_f
        elif mode_select == 'in_store':
            self.select = self.classe_in_s

        elif mode_select == 'has_pk':
            self.select = self.obj_has_pk
        elif mode_select == 'has_schema':
#            print ("mode select has schema")
            self.select = self.obj_has_schema
        elif mode_select == 'has_couleur':
            self.select = self.sel_couleur
        elif mode_select == 'has_geom':
            self.select = self.sel_geom
        elif mode_select == 'has_geomv':
            self.select = self.sel_geomv

        elif mode_select == 'false':
            self.select = self.false

        elif mode_select == 'regex':
            self.select = self.triclasse
        elif mode_select == 'exist':
            self.select = self.valexiste
        elif mode_select == 'pexist':
            self.select = self.pexiste
        elif mode_select == 'peval':
            self.select = self.peval
        elif mode_select == 'ceval':
#            print ('dans ceval', self.attribut, self.valeurs)
            self.select = self.false
            if self.attribut == self.valeurs:
                self.select = self.true
        elif mode_select == 'cereg':
            self.select = self.false
            if self.valeurs.search(self.attribut):
                self.select = self.true
        elif mode_select == 'is_pk':
            self.select = self.att_is_pk
        elif mode_select == 'is_2D':
            self.select = self.obj_is_2d
        elif mode_select == 'is_3D':
            self.select = self.obj_is_3d
        elif mode_select == 'is_ko':
            self.select = self.obj_is_ko
        elif mode_select == 'is_ok':
            self.select = self.obj_is_ok
        elif mode_select == 'is_null':
            self.select = self.att_is_null
        elif mode_select == 'is_not_null':
            self.select = self.att_not_null
        elif mode_select == 'is_virtuel':
            self.select = self.obj_is_virtuel
        elif mode_select == 'is_not_virtuel':
            self.select = self.obj_not_virtuel
        elif mode_select == 'changed':
            self.select = self.fsel_changed
        elif mode_select == 'calc':
# permet des comparaisons sur les attributs en mode numerique ou caractère'''
#            if "N: " in valeurs:
#                exp_final = valeurs.replace("N: ", "N:"+attribut)
#                # on doit passeren mode numerique:
#                tmp = re.split("([<>!=]+)",exp_final,1)
#                exp_final = "float("+tmp[0]+")"+tmp[1]+"float("+tmp[2]+")"

            exp_final = re.sub("^ *N:(?!#?[A-Za-z])", "N:"+attribut, valeurs)
            exp_final = re.sub("^ *C:(?!#?[A-Za-z])", "C:"+attribut, exp_final)

#            exp_final = exp_final.replace("C:", "C:"+attribut)
#            print('exp test final', exp_final, attribut, valeurs)

            self.fonction = compilefonc(exp_final, 'obj', debug=debug)
            self.select = self.lambdaselect
        else:
            print("mode selection inconnu", mode_select)
            self.select = self.false
#        print ('mode select retenu', mode_select,attribut,valeurs,negation)
        if negation:
#            print('selection negative', self.attribut)
            self.fonction2 = self.select
            self.select = lambda x: not self.fonction2(x)

#    def fselect(self, obj):
#        '''fonction de selection'''
#        attr = obj.attributs
#        regle = self.regle
##        print ("dans fselect", self.expselect)
#        return eval(self.expselect)
    def lambdaselect(self, obj):
        """fonction generique en tant que selecteur"""
#        print("dans lambdaselect ")
        return self.fonction(obj)

#    def fselN3D(self, _):
#        '''fonction de comparaison de coordonnees Z'''
#        return eval(self.s3D)
#
#    def fselC3D(self, valeur):
#        ''' comparaison caracteres '''
#        if self.val_tri is None:
#            return False
#        return self.val_tri.search(valeur)

    def fsel_changed(self, obj):
        '''fonction de detection de changement d une valeur'''
        if self.precedent != obj.attributs.get(self.attribut):
            self.precedent = obj.attribut.get(self.attribut)
            return True
        return False

    def id_regex(self, obj):
        """selection sur l identifiant de classe"""
        niveau, classe = obj.ident
        return self.valeurs.search(niveau+'.'+classe)

    def obj_is_ko(self, obj):
        '''verification si la precedente operation s'est mal passe'''
#        print ('dans ko',not obj.ok)
        return not obj.is_ok

    def obj_is_ok(self, obj):
        '''verification si la precedente operation s'est mal passe'''
        return obj.is_ok

    def pexiste(self, _):
        ''' test d'existance d'un parametre '''
        return self.stock_param.get_param(self.attribut)

    def peval(self, _):
        ''' test de valeur d'un parametre '''
#        print ('test peval',self.attribut,self.stock_param.get_param(self.attribut),self.valeurs)
        return self.stock_param.get_param(self.attribut) == self.valeurs

    def valexiste(self, obj):
        ''' test d'existance d'attribut sur le code classe'''
        #print ("valexiste:",self.attribut,obj.attributs,self.attribut in obj.attributs)
        return self.attribut in obj.attributs

    def triclasse(self, obj):
        ''' recherche d'une sequence dans un attribut'''
        return self.valeurs.search(obj.attributs.get(self.attribut, ""))

    def classe_in_f(self, obj):
        ''' vrai si le contenu d'un attribut est dans une liste
    mode dynamique : la liste depend du repertoire contenant les donnees'''
#        return self.est_dans(self.fichier, obj.attributs.get("#repertoire",''),
#                                obj.attributs.get(self.code_classe, ""))
        return obj.attributs.get(self.attribut, "").strip() in Selecteur.dynlists[self.valeurs]

#    def classe_in_store(self, obj):
#        ''' vrai si le contenu d'un attribut est dans une liste stockee'''
#   #        return self.est_dans(self.fichier, obj.attributs.get("#repertoire",''),
##                                obj.attributs.get(self.code_classe, ""))
#        return obj.attributs.get(self.attribut, "").strip() in self.valeurs
#

    def classe_in_s(self, obj):
        ''' vrai si le contenu d'un attribut est dans une liste
        mode statique : la liste depend du repertoire contenant les donnees'''
#        print("regles: --------------------------->select in ", self.code_classe,
#              obj.attributs.get(self.code_classe,""),self.fichier)
#        print ("selecteur",self.regle.numero,self.regle.fichier,self.fichier)
#        if debug:
#        print ('-----------selecteur a:', self.attribut,'c:',
#               obj.attributs.get(self.attribut,"").strip(),'v:',self.valeurs)
        return obj.attributs.get(self.attribut, "").strip() in self.valeurs

    def vals_in_s(self, obj):
        ''' vrai si le contenu d'un ensemble d'attributs est dans une liste
        mode statique : la liste depend du repertoire contenant les donnees'''
#        print("regles: --------------------------->select in ", self.code_classe,
#              obj.attributs.get(self.code_classe,""),self.fichier)
#        print ("selecteur",self.regle.numero,self.regle.fichier,self.fichier)
#        if debug:
#        print ('-----------selecteur a:', self.attribut,'c:',
#               obj.attributs.get(self.attribut,"").strip(),'v:',self.valeurs)
        rech = ';'.join([obj.attributs.get(i, "") for i in self.attribut]).strip()
        return rech in self.valeurs




    def classe_in_a(self, obj):
        ''' vrai si un des attributs porte le nom de la classe
    mode statique : la liste depend du repertoire contenant les donnees'''
        return obj.attributs.get(self.attribut, "").strip() in obj.attributs

    def obj_has_pk(self, obj):
        ''' vrai si on a defini un des attributs comme clef primaire
         le test est fait sur le premier objet de  la classe qui arrive
         et on stocke le resultat : pur eviter que des modifas ulterieures de
         schema ne faussent les tests'''
        clef = obj.ident
#        if obj.schema:
#            print ('selecteurs: dans has_pk : pk : ', obj.schema.haspkey(), obj.schema.indexes)
#        else:
#            print ('selecteurs: dans has_pk objet sans schema')
        if clef in self.schemaqueries:
            return self.schemaqueries[clef]
#        if obj.schema:
        self.schemaqueries[clef] = obj.schema and obj.schema.haspkey
        return self.schemaqueries[clef]
#        self.schemaqueries[clef]=0
#        return self.schemaqueries[clef]

    def att_is_pk(self, obj):
        '''vrai si l'attribut est une clef primaire
        le test est fait sur le premier objet de  la classe qui arrive
        et on stocke le resultat : pur eviter que des modifas ulterieures de
        schema ne faussent les tests'''

        clef = obj.ident+(self.attribut,)
        if clef in self.schemaqueries:
            return self.schemaqueries[clef]
#        if obj.schema:
        self.schemaqueries[clef] = obj.schema.indexes.get("P:1") == self.attribut
        return self.schemaqueries[clef]
#        self.schemaqueries[clef]=0
#        return False
    @staticmethod
    def obj_is_virtuel(obj):
        '''vrai si l'objet est virtuel'''
#        print ('selecteurs: dans virtuel :', obj.ident,obj.virtuel)
        return obj.virtuel

    @staticmethod
    def obj_is_2d(obj):
        '''vrai si l'objet est virtuel'''
#        print ('selecteurs: dans virtuel :', obj.ident,obj.virtuel)
        return obj.dimension == 2

    @staticmethod
    def obj_is_3d(obj):
        '''vrai si l'objet est virtuel'''
#        print ('selecteurs: dans virtuel :', obj.ident,obj.virtuel)
        return obj.dimension == 3

    @staticmethod
    def obj_has_schema(obj):
        '''vrai si l'objet a un schema'''
#        print ("dans hasschema")
        return obj.schema and obj.schema.stable

    def obj_not_virtuel(self, obj):
        '''vrai si l'objet est virtuel'''
        return not obj.virtuel

    def att_is_null(self, obj):
        '''vrai si l'attribut existe et est null'''
        return  not obj.attributs.get(self.attribut, False)

    def att_not_null(self, obj):
        '''vrai si l'attribut est non null'''
        return obj.attributs.get(self.attribut, False)

    def sel_couleur(self, obj):
        '''vrai si une couleur est presente dans la geometrie'''
#        print('recherche_couleur',self.cnum)
        return obj.geom_v.has_couleur(self.cnum)


    def sel_geom(self, obj):
        '''vrai si l'objet a un attribut geometrique '''
        return bool(obj.geom)

    def sel_geomv(self, obj):
        '''vrai s'il a une geometrie valide'''
        return obj.geom_v.valide
# fonctions de selections dans un hstore
    @staticmethod
    def __htodic(hstore):
        """convertit un hstore en dict"""
        return {i.split('" => "') for i in hstore.split('", "')}

    def hselk(self, obj):
        '''selection sur une valeur dans une clef d'un hstore'''
        if self.attribut not in obj.hdict:
            obj.hdict[self.attribut] = self.__htodic(obj.attributs.get(self.attribut))
        return self.valeurs in obj.hdict[self.attribut]

    def hselv(self, obj):
        '''selection sur une valeur dans une valeur d'un hstore'''
        if self.attribut not in obj.hdict:
            obj.hdict[self.attribut] = self.__htodic(obj.attributs.get(self.attribut))
        return self.valeurs in obj.hdict[self.attribut].values()

    def hselvk(self, obj):
        '''selection sur une valeur dans une valeur d'un hstore'''
        if self.attribut not in obj.hdict:
            obj.hdict[self.attribut] = self.__htodic(obj.attributs.get(self.attribut))
        return obj.hdict[self.attribut].get(self.valeurs[0]) == self.valeurs[1]
