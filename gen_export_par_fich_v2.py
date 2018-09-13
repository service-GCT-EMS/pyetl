# genere les scripts d'export de la base
import sys,os
import shutil
maxpar=1
menage=0
facteur=1

def charge_site_params():
    ''' charge des definitions de variables liees au site '''
    site_params_def=os.environ.get('PYETL_SITE_PARAMS')
    if not site_params_def:
        print ('gen_export: pas de parametres locaux')
        return
    CONFIGFILE = os.path.join(site_params_def,'export_parametres.csv')
    nom=''
    site_params=dict()
    for cf in open(CONFIGFILE, 'r').readlines():
        l=(cf[:-1]+';;;').split(';')
        if l and l[0] and l[0][0]=='!':
            continue
        if l and l[0]=='&&#set':
            nom=l[1]
            site_params[nom]=list()
        else:
            if nom:
#               print ('parametres de site ',nom,l)
                valeur=l[1].strip()
                variable=l[0].strip()
                if len(valeur)>0 and valeur[0]=='$':
                    valeur=os.environ.get(valeur[1:],l[2])
                site_params[nom].append((variable,valeur))
    return site_params

def stocke_param(stock, parametre,site_params):
    '''stockage d'un parametre'''
    if "=" in parametre:
        par = parametre.split("=",1)
        if par[0]=='config':
            stock.update(site_params.get(par[1]))
        if len(par)<2:
            par.append('')
        if par[1]=='""' :
            par[1]=''
        stock[par[0]] = par[1]
    

def lire_schema_csv(fichier_classes,liste_classes,liste_schemas):
    for i in open(fichier_classes,'r'):
        if i[0]=='!' : continue
        v=i.split(';')
        liste_classes[v[1]]=v[4]
        liste_schemas[v[1]]=v[0]

def crerepvide(rep):
    try:
        shutil.rmtree(rep,True)
        os.mkdir(rep)
    except:
        pass


def crerep(nom,vide=False):
    '''creation d'une arborescence de repertoires'''
    if not nom:
        return False
    if os.path.exists(nom):
        if vide:
            shutil.rmtree(nom,True)
            return crerep(nom)
        return True
    crerep(os.path.dirname(nom))
    try:
        os.mkdir(nom)
        return True
    except OSError:
        print ('gen_export: creation repertoire impossible:',nom)
        return False




def init_reps(maxpar,facteur,rep_export,log_export):
    for i in range(maxpar):    # on cree les repertoires
        #batch.append(open("../donnees/scripts/export_"+str(i)+".bat","w"))
        if not os.path.exists(rep_export+"\\Dx"+str(i)) : os.mkdir(rep_export+"\\Dx"+str(i))
    
    multi=facteur * maxpar
    batch=dict()
    for i in range(multi):    # export 
        #batch.append(open("../donnees/scripts/export_"+str(i)+".bat","w"))
        batch[i]=(open(rep_travail+"/export_"+str(i)+".bat","w"))
        batch[i].write("set PATH="+path+";%PATH%\n")
        batch[i].write("set ORACLE_HOME="+orahome+"\n")
        fich_fin=rep_travail+"\\fin"+str(i)
        if os.path.isfile(fich_fin):os.remove(fich_fin) # menage initial
    return batch

        












parms={'classes':'',
       'travail':'',
       'export':'',
       'import':'',
       'scripts':'',
       'prog_traitement'
       'param_traitement':'',
       'params':'',
       'log':'',
       'prog_export':'',
       'nb_process':'',
       'menage':'',
       'multiplicateur':'',
       'base':'',
       'service':'',
       'user':'',
       'passwd':'',
       'groupage':'classe',
       'path':r'c:\util\ora10g\bin',
       'orahome':r'C:\util\ora10g'}


if len(sys.argv)>1:
    site_params=charge_site_params()
    for i in sys.argv[1:]:
        stocke_param(parms,i,site_params)
else :
    print("usage "+ sys.argv[0]+ " config=nom [parametre=valeur ...]")
    sys.exit(1)
    
print ('gen_export: parametres de traitement\n','\n'.join([i + ' -> ' +parms[i] for i in parms]))
fichier_classes=parms['classes']
rep_travail=parms['travail']
rep_export=parms['export']
rep_import=parms['import']
rep_scripts=parms['scripts']
prog_mapper=parms['prog_traitement']
traitement=parms['param_traitement']
param_compl=parms['params']
exporteur=parms['prog_export']
log=parms['log']
log_export=os.path.join(log,'export')
maxpar=int(parms['nb_process'])
facteur=int(parms['multiplicateur'])
menage=parms['menage']
user=parms['user']
passwd=parms['passwd']
base=parms['base']
service=parms['service']
path=parms['path']
orahome=parms['orahome']
groupage=parms['groupage']
multi=facteur * maxpar    

#fichier_classes = 'classes_elyx.csv'

vide=False
if menage=='oui':
    print('menage ')
    vide=True
crerep(rep_export,vide=vide)
crerep(rep_import,vide=vide)
crerep(log_export,vide=vide)
crerep(rep_travail+"\\xml",vide=vide)
for i in range(multi):
    crerep(os.path.join(log_export,'log_fea_'+str(i)),vide=vide)

    
liste_classes=dict()
liste_schemas=dict()
lire_schema_csv(fichier_classes,liste_classes,liste_schemas)

multi=maxpar*facteur

batch=init_reps(maxpar,facteur,rep_export,log_export)





if groupage=='niveau':
    
    
    groupes=dict()
    
    
    
    
    
    for i in liste_classes:
        liste=groupes.setdefault(liste_schemas[i],[])
        liste.append(i)
    
    taille=dict()
    nf=dict()            
    for i in groupes: 
        taille[i]=sum([int(liste_classes[j]) for j in groupes[i]])
        
    for i in list(groupes.keys()): # decoupage 2eme niveau si necessaire
        if taille[i]>2000000:
            bigliste=groupes[i]
            print("decoupage ", i, taille[i])
            del groupes[i]
            for j in bigliste:
               l=j.split("_")
               liste=groupes.setdefault(i+'_'+l[0],[])
               liste.append(j) 
    
    taille=dict()                       
    for i in groupes: 
        taille[i]=sum([int(liste_classes[j]) for j in groupes[i]])
        nf[i]=len(groupes[i])

    # calcul des regroupements
    dest=dict()
    taillebatch=[0]*maxpar
    for g in sorted(list(groupes.keys()),key=taille.get,reverse=True):
        imin=0
        for i in range(maxpar):
            if taillebatch[i]<taillebatch[imin]: imin=i
        taillebatch[imin]+=taille[g]
        dest[g]=imin
    v=0
    for g in sorted(list(groupes.keys()),key=taille.get,reverse=True):
        for classe in sorted(groupes[g]):
            v=(v+1)%multi
            nom=rep_travail+"\\xml\\export_"+g+'_'+classe+".xml"
            sortie=open(nom,"w")
            sortie.write('<Ora2FeaConfig>\n <oraCnx cnx="'+service+'" user="'+user+'" pwd="'+passwd+'" role="" />\n')
            sortie.write('<apicBase name="'+base+'" version="5"/>\n<filePath>\n')
            sortie.write('<dstFile path="'+rep_export+'\\Dx'+str(dest[g])+'\\'+g+'\\'+classe+'"/>\n') 
            sortie.write('<logDir path="'+log_export+'\\log_fea_'+str(v)+'"/>\n</filePath>\n')
            sortie.write('<classes list="'+classe+'"/>\n')
            sortie.write('<coordinateSystem value="0"/> \n</Ora2FeaConfig> \n')
            sortie.close()
            batch[v].write(exporteur+' -c ".\\'+nom+'"\n')


else: # pas de groupagee logique (optimisation maximale)
    taille_export=[0]*multi
    taille_trait=[0]*maxpar
    print ('gen_export: optimisation maxi sur ',len(liste_classes),'classes' )
    print ('gen_export: processus_export',multi,'traitement',maxpar)

    for classe in sorted(liste_classes.keys(),key=lambda i : int(liste_classes[i]),reverse=True):
        if int(liste_classes[classe]) > 0: 
#            print (liste_schemas[classe],classe,int(liste_classes[classe]))
            tt=int(liste_classes[classe])
            te=tt+50000
            imin=0
            for i in range(multi):
                if taille_export[i]<taille_export[imin]: imin=i
            taille_export[imin]+=te
            exp=imin
            imin=0
            for i in range(maxpar):
                if taille_trait[i]<taille_trait[imin]: imin=i
            taille_trait[imin]+=tt
            trait=imin
            g=liste_schemas[classe]
#            print ('traitement',g,classe,exp,trait)
            nom=rep_travail+"\\xml\\export_"+g+'_'+classe+".xml"
            sortie=open(nom,"w")
            sortie.write('<Ora2FeaConfig>\n <oraCnx cnx="'+service+'" user="'+user+'" pwd="'+passwd+'" role="" />\n')
            sortie.write('<apicBase name="'+base+'" version="5"/>\n<filePath>\n')
            sortie.write('<dstFile path="'+rep_export+'\\Dx'+str(trait)+'\\'+g+'\\'+classe+'"/>\n') 
            sortie.write('<logDir path="'+log_export+'\\log_fea_'+str(exp)+'"/>\n</filePath>\n')
            sortie.write('<classes list="'+classe+'"/>\n')
            sortie.write('<coordinateSystem value="0"/> \n</Ora2FeaConfig> \n')
            sortie.close()
            if ':' in nom: # c'est un chemin absolu
                batch[exp].write(exporteur+' -c "'+nom+'"\n')
            else:
                batch[exp].write(exporteur+' -c ".\\'+nom+'"\n')
        else:
            pass
#            print ('classe vide',liste_classes[classe])


    

        

expo_total=open(rep_travail+"/export_total.bat","w")
traitement_total=open(rep_travail+"/mapper_total.bat","w")
expo_total.write("echo export total de la base\n")
for i in range(multi):
    batch[i].write("echo fin > "+os.path.join(rep_travail,"fin"+str(i)+'\n'))
    batch[i].write("exit\n")
    batch[i].close()
    expo_total.write("start "+os.path.join(rep_travail,"export_"+str(i)+'\n'))
    
for i in range(maxpar):
    nom_unit=rep_travail+"/mapper_"+str(i)+".bat"
    traitement_unitaire=open(nom_unit,"w")
    tu=' '.join((prog_mapper,os.path.join(rep_scripts,traitement),
                 os.path.join(rep_export,"Dx"+str(i)),rep_import,
                 'n='+str(i),'script='+rep_scripts,'travail='+rep_travail,
                 'param='+param_compl,
                 '>', os.path.join(log,"log_mapper"+str(i)+".txt\n")
                 ))
    traitement_unitaire.write(tu)
    traitement_unitaire.write("exit\n")
    traitement_unitaire.close()
    traitement_total.write("start "+os.path.join(rep_travail,"mapper_"+str(i)+'\n'))
    
    
expo_total.write("exit\n")
traitement_total.write("exit\n")
expo_total.close()    
traitement_total.close()    
print('traitement termine')