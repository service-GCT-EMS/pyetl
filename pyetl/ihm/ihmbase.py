# -*- coding: utf-8 -*-


# Form implementation generated from reading ui file 'Dialog.ui'
#
# Created: Tue May 24 10:26:21 2011
#      by: PyQt4 UI code generator 4.8.4
#


import sys
#sys.path.append("D:\\appl\\winapp32\\PYTHON\\Lib\\site-packages")
import sip
sip.setapi('QString', 2)

from PyQt4 import QtCore, QtGui


#import csv
import os


def ligne_choix_fichier(parent,nom,texte,position):
    
    base=QtGui.QWidget(parent)
    base.setGeometry(QtCore.QRect(position))
    base.setObjectName(nom+'__base')
    bloc=QtGui.QVBoxLayout(base)
    bloc.setMargin(0)
    bloc.setObjectName(nom+'__bloc')
    lignetexte = QtGui.QLabel(base)
    lignetexte.setObjectName(nom+'__texte')
    lignetexte.setText(texte)
    bloc.addWidget(lignetexte) 
    
    ligne_entree=QtGui.QLineEdit(base)
    ligne_entree.setObjectName(nom+'__entree')
    
    fichier_entree = QtGui.QPushButton("QFileDialog.get&OpenFileName()")
    fichier_entree.setEnabled(True)
    fichier_entree.setMinimumSize(QtCore.QSize(25, 25))
    fichier_entree.setMaximumSize(QtCore.QSize(25, 25))
    fichier_entree.setObjectName(nom+'__bouton')
    
    
    
    self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
    self.verticalLayoutWidget = QtGui.QWidget(self)
    self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 481, 51))
    self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

    self.Entree = QtGui.QVBoxLayout(self.verticalLayoutWidget)
    self.Entree.setMargin(0)
    self.Entree.setObjectName("Entree")
    
    self.entree = QtGui.QLabel(self.verticalLayoutWidget)
    self.entree.setObjectName("entree")
    
    self.Entree.addWidget(self.entree)   
    if self.stock_param.entree:
        if self.stock_param.entree == '-': # traitement sans entree 
            self.entree.setText("traitement sans entree")
        else : 
            self.entree.setText("entrée : " + self.stock_param.entree)
    else:
        self.entree.setText("choisissez les données en entrée")
        self.line_fichier_entree = QtGui.QLineEdit(self.verticalLayoutWidget_3)
        self.line_fichier_entree.setObjectName("line_fichier_entree")
        
        self.horizontalLayout.addWidget(self.line_fichier_entree)

        # Définition du bouton "choix du fichier en entrée"
        self.fichier_entree = QtGui.QPushButton("QFileDialog.get&OpenFileName()")
        self.fichier_entree.setEnabled(True)
        self.fichier_entree.setMinimumSize(QtCore.QSize(25, 25))
        self.fichier_entree.setMaximumSize(QtCore.QSize(25, 25))
        self.fichier_entree.setObjectName("fichier_entree")










##try:
##    _fromUtf8 = QtCore.QString.fromUtf8
##except AttributeError:
##    _fromUtf8 = lambda s: s
class Auto_ui(QtGui.QDialog):
    def __init__(self, stock_param, parent=None):
        super(Ui_Transfo, self).__init__(parent)
        self.stock_param=stock_param
        self.setObjectName("pyetl")
        self.setWindowModality(QtCore.Qt.NonModal)
        self.resize(500, 380)
        self.setMinimumSize(QtCore.QSize(500, 380))
        self.setMaximumSize(QtCore.QSize(500, 380))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'icone.jpg')), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.setModal(False)  
        # défintion des boutons OK et Fermer
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(320, 340, 171, 32))
        self.buttonBox.setMouseTracking(False)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")        
        # definition de la ligne de choix de l'entree 
 # -------------------- entree ---------------------------       
        self.verticalLayoutWidget = QtGui.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 481, 51))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

        self.Entree = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.Entree.setMargin(0)
        self.Entree.setObjectName("Entree")
        
        self.entree = QtGui.QLabel(self.verticalLayoutWidget)
        self.entree.setObjectName("entree")
        
        self.Entree.addWidget(self.entree)   
        if self.stock_param.entree:
            if self.stock_param.entree == '-': # traitement sans entree 
                self.entree.setText("traitement sans entree")
            else : 
                self.entree.setText("entrée : " + self.stock_param.entree)
        else:
            self.entree.setText("choisissez les données en entrée")
            self.line_fichier_entree = QtGui.QLineEdit(self.verticalLayoutWidget_3)
            self.line_fichier_entree.setObjectName("line_fichier_entree")
            
            self.horizontalLayout.addWidget(self.line_fichier_entree)
    
            # Définition du bouton "choix du fichier en entrée"
            self.fichier_entree = QtGui.QPushButton("QFileDialog.get&OpenFileName()")
            self.fichier_entree.setEnabled(True)
            self.fichier_entree.setMinimumSize(QtCore.QSize(25, 25))
            self.fichier_entree.setMaximumSize(QtCore.QSize(25, 25))
            self.fichier_entree.setObjectName("fichier_entree")

        # definition de la ligne de choix de la sortie  
 # -------------------- sortie ---------------------------       
        self.verticalLayoutWidget_2 = QtGui.QWidget(self)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 481, 51))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget")

        self.Sortie = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.Sortie.setMargin(0)
        self.Sortie.setObjectName("Sortie")
        
        self.sortie = QtGui.QLabel(self.verticalLayoutWidget)
        self.sortie.setObjectName("sortie")
        
        self.Sortie.addWidget(self.sortie)   
    
        if self.stock_param.sortie:
            if self.stock_param.sortie =='-': # traitement sans sortie 
                self.sortie.setText("traitement sans sortie")
            else : 
                self.sortie.setText("sortie : " + self.stock_param.entree)
        else:
            self.sortie.setText("choisissez les données en entrée")
            self.line_fichier_sortie = QtGui.QLineEdit(self.verticalLayoutWidget_3)
            self.line_fichier_sortie.setObjectName("line_fichier_sortie")
            
            self.horizontalLayout.addWidget(self.line_fichier_entree)
    
            # Définition du bouton "choix du fichier en entrée"
            self.fichier_sortie = QtGui.QPushButton("QFileDialog.get&OpenFileName()")
            self.fichier_sortie.setEnabled(True)
            self.fichier_sortie.setMinimumSize(QtCore.QSize(25, 25))
            self.fichier_sortie.setMaximumSize(QtCore.QSize(25, 25))
            self.fichier_sortie.setObjectName("fichier_entree")
            
        if self.stock_param.fichier_regles:
            if self.stock_param.sortie =='-': # traitement sans sortie 
                self.sortie.setText("traitement sans sortie")
            else : 
                self.sortie.setText("sortie : " + self.stock_param.entree)
        else:
            self.sortie.setText("choisissez les données en entrée")
            self.line_fichier_sortie = QtGui.QLineEdit(self.verticalLayoutWidget_3)
            self.line_fichier_sortie.setObjectName("line_fichier_sortie")
            
            self.horizontalLayout.addWidget(self.line_fichier_entree)
    
            # Définition du bouton "choix du fichier en entrée"
            self.fichier_sortie = QtGui.QPushButton("QFileDialog.get&OpenFileName()")
            self.fichier_sortie.setEnabled(True)
            self.fichier_sortie.setMinimumSize(QtCore.QSize(25, 25))
            self.fichier_sortie.setMaximumSize(QtCore.QSize(25, 25))
            self.fichier_sortie.setObjectName("fichier_entree")




")

class Ui_Transfo(QtGui.QDialog):
    
    def __init__(self, parent=None):
        super(Ui_Transfo, self).__init__(parent)

        # défintion générale du programme
        self.setObjectName("Transfo")
        self.setWindowModality(QtCore.Qt.NonModal)
        self.resize(500, 380)
        self.setMinimumSize(QtCore.QSize(500, 380))
        self.setMaximumSize(QtCore.QSize(500, 380))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images_terre.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.setModal(False)

        # défintion des boutons OK et Fermer
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(320, 340, 171, 32))
        self.buttonBox.setMouseTracking(False)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")        
        
        self.verticalLayoutWidget = QtGui.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 481, 51))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        
        self.Entree = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.Entree.setMargin(0)
        self.Entree.setObjectName("Entree")
        
        self.entree = QtGui.QLabel(self.verticalLayoutWidget)
        self.entree.setObjectName("entree")
        
        self.Entree.addWidget(self.entree)

        # Définition de la liste de choix "entrée"
        self.entree_2 = QtGui.QComboBox(self.verticalLayoutWidget)
        self.entree_2.setObjectName("entree_2")
        self.entree_2.addItem("")
        self.entree_2.addItem("")
        self.entree_2.addItem("")
        self.entree_2.addItem("")
        self.entree_2.addItem("")
        
        self.Entree.addWidget(self.entree_2)
        
        self.verticalLayoutWidget_2 = QtGui.QWidget(self)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 210, 481, 51))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")

        self.Sortie = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.Sortie.setMargin(0)
        self.Sortie.setObjectName("Sortie")
        
        self.sortie = QtGui.QLabel(self.verticalLayoutWidget_2)
        self.sortie.setObjectName("sortie")
        
        self.Sortie.addWidget(self.sortie)

        # Définition de la liste de choix "sortie"     
        self.sortie_2 = QtGui.QComboBox(self.verticalLayoutWidget_2)
        self.sortie_2.setObjectName("sortie_2")
        self.sortie_2.addItem("")
        self.sortie_2.setItemText(0,u"NTF - Lambert 69 (syst\u00E8me local CUS)")

        self.Sortie.addWidget(self.sortie_2)
        
        self.verticalLayoutWidget_3 = QtGui.QWidget(self)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(10, 70, 481, 51))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")

        self.Fichier_entree = QtGui.QVBoxLayout(self.verticalLayoutWidget_3)
        self.Fichier_entree.setMargin(0)
        self.Fichier_entree.setObjectName("Fichier_entree")

        self.label = QtGui.QLabel(self.verticalLayoutWidget_3)
        self.label.setObjectName("label")
        
        self.Fichier_entree.addWidget(self.label)

        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Définition de la ligne de texte "choix du fichier en entrée"
        self.line_fichier_entree = QtGui.QLineEdit(self.verticalLayoutWidget_3)
        self.line_fichier_entree.setObjectName("line_fichier_entree")
        
        self.horizontalLayout.addWidget(self.line_fichier_entree)

        # Définition du bouton "choix du fichier en entrée"
        self.fichier_entree = QtGui.QPushButton("QFileDialog.get&OpenFileName()")
        self.fichier_entree.setEnabled(True)
        self.fichier_entree.setMinimumSize(QtCore.QSize(25, 25))
        self.fichier_entree.setMaximumSize(QtCore.QSize(25, 25))
        self.fichier_entree.setObjectName("fichier_entree")

        self.horizontalLayout.addWidget(self.fichier_entree)
        
        self.Fichier_entree.addLayout(self.horizontalLayout)

        # Définition du texte expliquant les formats
        self.format = QtGui.QLabel(self)
        self.format.setGeometry(QtCore.QRect(10, 130, 479, 65))
        self.format.setObjectName("format")
   
        self.verticalLayoutWidget_4 = QtGui.QWidget(self)
        self.verticalLayoutWidget_4.setGeometry(QtCore.QRect(10, 270, 481, 51))
        self.verticalLayoutWidget_4.setObjectName("verticalLayoutWidget_4")
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget_4)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.label_2 = QtGui.QLabel(self.verticalLayoutWidget_4)
        self.label_2.setObjectName("label_2")
        
        self.verticalLayout.addWidget(self.label_2)
        
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        # Définition de la ligne de texte "choix du fichier en sortie"
        self.line_fichier_sortie = QtGui.QLineEdit(self.verticalLayoutWidget_4)
        self.line_fichier_sortie.setObjectName("line_fichier_sortie")

        self.horizontalLayout_2.addWidget(self.line_fichier_sortie)

        # Définition du bouton "choix du fichier en sortie"
        self.fichier_sortie = QtGui.QPushButton("QFileDialog.get&SaveFileName()")
        self.fichier_sortie.setMinimumSize(QtCore.QSize(25, 25))
        self.fichier_sortie.setMaximumSize(QtCore.QSize(25, 25))
        self.fichier_sortie.setObjectName("fichier_sortie")
        
        self.horizontalLayout_2.addWidget(self.fichier_sortie)
        
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        # Définition du texte indiquant l'auteur
        self.label_3 = QtGui.QLabel(self)
        self.label_3.setGeometry(QtCore.QRect(10, 340, 261, 31))
        self.label_3.setObjectName("label_3")


        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.traitement)                    # lancement sur clic bouton OK de "taitement"
        self.fichier_entree.clicked.connect(self.setOpenFileName)                                               # lancement sur clic bouton ... entrée de "setOpenFileName"
        self.fichier_sortie.clicked.connect(self.setSaveFileName)                                               # lancement sur clic bouton ... sortie de "setSaveFileName"
        QtCore.QObject.connect(self.entree_2, QtCore.SIGNAL("currentIndexChanged(int)"), self.choix_sortie)     # action lors du changement du choix dans la liste en entée
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.close)                         # fermeture du programme sur clic bouton Fermer
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):# Défintion des textes
        self.setWindowTitle(u"mapper 5 conversion de donnees")
        self.entree.setText("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Système de coordonnées en entrée :</span></p></body></html>")
        self.entree_2.setItemText(0, u"NTF - Lambert 1 (IGN)")
        self.entree_2.setItemText(1, u"NTF - Lambert 69 (syst\u00E8me local CUS)")
        self.entree_2.setItemText(2, u"RGF93 - CC48")
        self.entree_2.setItemText(3, u"RGF93 - CC49")
        self.entree_2.setItemText(4, u"WGS84 en coordonn\u00E9es cart\u00E9siennes")
        self.sortie.setText("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Système de coordonnées en sortie :</span></p></body></html>")
        self.format.setText("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Pour des coordonnées planes, le formattage du fichier doit être le suivant :</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Numéro  Est  Nord (sep:tabulation)</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Pour des coordonnées cartésiennes (système WGS84), le formattage du fichier doit être le suivant :</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Numéro  X  Y  Z (sep:tabulation)</span></p></body></html>")
        self.label.setText(u"Choisir le fichier \u00E0 transformer :")
        self.line_fichier_entree.setToolTip(u"Emplacement et nom du fichier \u00E0 transformer")
        self.fichier_entree.setText("...")
        self.label_2.setText("Choisir l\'emplacement du fichier en sortie :")
        self.line_fichier_sortie.setToolTip("Emplacement et nom du fichier en sortie")
        self.fichier_sortie.setText("...")
        self.label_3.setText("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-style:italic;\">Service de l\'Information Géographique</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-style:italic;\">Communauté Urbaine de Strasbourg</span></p></body></html>")




    def setOpenFileName(self):# Boîte de dialogue "choisir fichier en entrée"
        options = QtGui.QFileDialog.Options()
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                u"Choisissez le fichier \u00E0 transformer",
                self.line_fichier_entree.text(),
                "All Files (*);;Text Files (*.txt)", options)
        if fileName:
            self.line_fichier_entree.setText(fileName)  # Ecriture du nom de fichier sur la ligne de texte

    def setSaveFileName(self):# Boîte de dialogue "choisir fichier en sortie"
        if len(self.line_fichier_entree.text())>0:
            self.line_fichier_sortie.setText(os.path.dirname(self.line_fichier_entree.text()))
        options = QtGui.QFileDialog.Options()
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                "Choisissez l'emplacement du fichier de sortie",
                self.line_fichier_sortie.text(),
                "Text Files (*.txt)", options)
        if fileName:
            self.line_fichier_sortie.setText(fileName)  # Ecriture du nom de fichier sur la ligne de texte

    def choix_sortie(self):# Changement des choix de la liste "sortie" en fonction des choix dans la liste "entrée"
        if self.entree_2.currentIndex()==0 :
            self.sortie_2.clear()
            self.sortie_2.addItem("")
            self.sortie_2.setItemText(0, u"NTF - Lambert 69 (syst\u00E8me local CUS)")
        elif self.entree_2.currentIndex()==1 :
            self.sortie_2.clear()
            self.sortie_2.addItem("")
            self.sortie_2.addItem("")
            self.sortie_2.addItem("")
            self.sortie_2.addItem("")
            self.sortie_2.setItemText(0, u"NTF - Lambert 1 (IGN)")
            self.sortie_2.setItemText(1, u"RGF93 - CC48")
            self.sortie_2.setItemText(2, u"RGF93 - CC49")
            self.sortie_2.setItemText(3, u"WGS84 en coordonn\u00E9es cart\u00E9siennes")
        elif self.entree_2.currentIndex()==2 :
            self.sortie_2.clear()
            self.sortie_2.addItem("")
            self.sortie_2.setItemText(0, u"NTF - Lambert 69 (syst\u00E8me local CUS)")
        elif self.entree_2.currentIndex()==3 :
            self.sortie_2.clear()
            self.sortie_2.addItem("")
            self.sortie_2.setItemText(0, u"NTF - Lambert 69 (syst\u00E8me local CUS)")
        elif self.entree_2.currentIndex()==4 :
            self.sortie_2.clear()
            self.sortie_2.addItem("")
            self.sortie_2.setItemText(0, u"NTF - Lambert 69 (syst\u00E8me local CUS)")

                          
    def traitement(self):# traitement des transformations de coordonnées


        
        en=self.entree_2.currentIndex()
        so=self.sortie_2.currentIndex()
        tr="" # type de traitement
        
    
        # test de rensignement des fichiers entrée / sortie

        if self.line_fichier_entree.text()=="" :
            QtGui.QMessageBox.critical(self,u'ERREUR',u'Veuillez renseigner l\u0027emplacement du fichier \u00E0 transformer')
            return()
        if self.line_fichier_sortie.text()=="" :
            QtGui.QMessageBox.critical(self,u'ERREUR',u'Veuillez renseigner l\u0027emplacement du fichier de sortie')
            return()

        if self.line_fichier_sortie.text()==self.line_fichier_entree.text():
            QtGui.QMessageBox.critical(self,u'ERREUR',u'Le fichier de sortie doit \u00EAtre diff\u00E9rent du fichier source')
            return()            
        
        # renseignement du sens, des projections, des coordonnées englobantes de contrôle et du type de traitement
        if en==0 :
            sens = 2
            sc_en='L1'
            xmin=970000
            xmax=1030000
            ymin=80000
            ymax=140000
            sc_so='L1'
            tr='cus'
        if en==1 :
            sens = 1
            sc_en='L1'
            xmin=970000
            xmax=1030000
            ymin=80000
            ymax=140000
            if so==0 :
                sc_so='L1'
                tr='cus'
            if so==1 :
                sc_so='CC48'
            if so==2 :
                sc_so='CC49'
            if so==3 :
                sc_so='WGS84'
                tr='wgs_s'
        if en==2 :
            sens = 2
            sc_en='CC48'
            xmin=2020000
            xmax=2080000
            ymin=7240000
            ymax=7310000
            sc_so='L1'
        if en==3 :
            sens = 2
            sc_en='CC49'
            xmin=2020000
            xmax=2080000
            ymin=8130000
            ymax=8200000
            sc_so='L1'
        if en==4 :
            sens = 2
            sc_en='WGS84'
            xmin=4160000
            xmax=4200000
            ymin=540000
            ymax=600000
            zmin=4740000
            zmax=4780000
            sc_so='L1'
            tr='wgs_e'
            
        compteur=1000
        compteur_pb=1000
#        fs=csv.writer(open(self.line_fichier_sortie.text(),'wb'),delimiter='\t')

        

        
        # indication de fin de traitement dans une boîte de dialoque
        QtGui.QMessageBox.information(self,u"Op\u00E9ration termin\u00E9e !",u"R\u00E9sultat du traitement :\n"+str(compteur)+u" point(s) transform\u00E9(s) correctement\n"+str(compteur_pb)+u" point(s) non transform\u00E9(s)")
        
        



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dialog = Ui_Transfo()
    sys.exit(dialog.exec_())


