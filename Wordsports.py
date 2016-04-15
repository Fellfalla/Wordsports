#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO: weight-vector serialiserien und abspeichern - dafür neue buttons
# TODO: neue schaltfläche um sources auszuwählen
# TODO: Eingebundene Sources anzeigen
# TODO: Umschalter reset nicht reset
# TODO: geschwindigkeit erhoehen

import sys
from GUI import Ui_Form
import GUI
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
import random
import string
from LearningModule import LearningModule

LEARNING_SOURCE = 'Names.txt'
DEPTH = 5
MIN_DEPTH = 1
LIMIT = 10**3
EPSILON = 3 # Potenz mit der die Worlänge eingeht
YOU_CAN_START = 'Let\'s Generate '
FIRST_THING_TO_DO = 'Please drop any Text'
CREATING_WEIGHT_VECTOR = 'Analysing Text Sources ...'
PROGRAM_TITLE = 'Messlattenpolizeipolizist'

class WorkThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.learner = LearningModule(EPSILON,LIMIT)

    def __del__(self):
        self.wait()

    def run(self,learner,path, remember, depth, minPartLength, epsilon):
        learner.createWeightVector(path, remember, depth, minPartLength, epsilon)
        return self.learner

class WordGenerator(QWidget):
    def __init__(self,parent=None):
        super(WordGenerator,self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        self.Wort = ''
        self.setAcceptDrops(True)
        
        QtCore.QObject.connect(self.ui.NextLetter, QtCore.SIGNAL(GUI._fromUtf8("clicked()")), self.generiereBuchstabe)
        QtCore.QObject.connect(self.ui.ResetLetter, QtCore.SIGNAL(GUI._fromUtf8("clicked()")), self.resetBuchstabe)
        QtCore.QObject.connect(self.ui.ResetLetter, QtCore.SIGNAL(GUI._fromUtf8("finished()")), self.resetBuchstabe)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowTitle(PROGRAM_TITLE)
        self.showText(CREATING_WEIGHT_VECTOR)
        self.ui.fileReminder.setChecked(True)
        self.ui.listWidget.clear()
        self.ui.Depth.setMinimum(self.ui.minPartLength.value())
        self.learner = LearningModule(EPSILON,LIMIT)
        self.showText(FIRST_THING_TO_DO)

        self.worker = WorkThread()

    def generiereBuchstabe(self):
        self.Wort = self.Wort + self.choiceMaker()
        if len(self.Wort) == 1:
            self.Wort = self.Wort.capitalize()
        self.showText(self.Wort)

    def choiceMaker(self):
        chances = {}
        chanceList = []
        for char in self.learner.letters:
            chances[char]=[0,char]
        if len(self.Wort) < 1:
            return random.choice(string.ascii_uppercase) #todo : Nur buchstaben verwenden, die in der Quelle vorkommen
        for wordPart in self.getWordParts():
            try:
                for char in self.learner.weightVector[wordPart]:
                    chances[char][0] = chances[char][0]+self.learner.weightVector[wordPart][char]
            except KeyError:
                pass
        #randomisieren
        for char in chances:
            chanceList.append([chances[char][0]*random.random(),chances[char][1]])
        self.printChanceList(chanceList)
        if max(chanceList)[0] == 0:
            return random.choice(['a','e','i','o','u'])
        else:
            return max(chanceList)[1] #   waehle das groeßte element und nimm dazugehoerigen buchstaben

    def printChanceList(self, chanceList):
        for Chance in sorted(chanceList)[::-1] :
            print ("%1s:%-4.f" %(Chance[1], Chance[0])," ")
        print('\n')

    def getWordParts(self):
        wordParts = []
        for i in range(1,DEPTH+1):
            try:
                wordParts.append(self.Wort[-i:].lower())
            except IndexError:
                pass
        return wordParts

    def resetBuchstabe(self):
        self.Wort = ''
        self.showText(self.Wort)

    def showText(self,text):
        self.ui.GeneratedWord.setText(str(text))
        self.update()

    def generateWeightVector(self,path):
        if self.ui.fileReminder.checkState():
            self.ui.listWidget.addItem(path)
        else:
            self.ui.listWidget.clear()
            self.ui.listWidget.addItem(path)
        self.Wort = ''
        self.learner.createWeightVector(path,self.ui.fileReminder.checkState(),self.ui.Depth.value(),self.ui.minPartLength.value(), self.ui.epsilon.value())
        #self.learner = self.worker.run(self.learner,path,self.ui.fileReminder.checkState(),self.ui.Depth.value(),self.ui.minPartLength.value(), self.ui.epsilon.value())
        if self.ui.saveWeightVector.isChecked():
            self.learner.saveWeightVector()
        self.showText(YOU_CAN_START)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText:
            self.showText(CREATING_WEIGHT_VECTOR)
            for url in event.mimeData().urls():
                path = url.toLocalFile()
            self.generateWeightVector(path)

        else:
            event.ignore()

    # def controlSpinValues(self):
    #     if self.ui.Depth.value() <
    #     self.ui.minPartLength.value()

#
# class MainForm(QtGui.QWindow):
#     def __init__(self, parent=None):
#         super(MainForm, self).__init__(parent)
#
#         self.wortsport = WordGenerator(self)
#         #self.connect(self.wortsport, QtCore.SIGNAL("dropped"), self.pictureDropped)
#         QtCore.QObject.connect(self.wortsport.ui.OK, QtCore.SIGNAL(GUI._fromUtf8("clicked()")), self.close)
#         self.setCentralWidget(self.wortsport)




def main(argv):
    """
    Einstiegspunkt
    """
    app = QtGui.QApplication(sys.argv)
    wortsport = WordGenerator()
    #wortsport.setWindowFlags(QSplashScreen)
    QtCore.QObject.connect(wortsport.ui.OK, QtCore.SIGNAL(GUI._fromUtf8("clicked()")), wortsport.close)
    wortsport.show()
    app.exec_()


if __name__ == "__main__":
    main(sys.argv)