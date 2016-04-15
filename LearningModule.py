#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
import pickle
import time
import codecs

class LearningModule:
    def __init__(self, epsilon=1/35, limit = 10, depth = 3, minPartLength = 1):
        self.wordList = []
        self.epsilon = epsilon
        self.limit = int(limit)
        self.increment = 1
        self.wordPartList = []
        self.wordPartToCharCounts = {}
        self.weightVector = {}
        self.letters = string.ascii_lowercase + ' '
        self.depth = depth
        self.minPartLength = minPartLength
        #print ("."+self.letters+".")

    def createWordPartList(self):
        # Create WordPartList and count next chars
        for word in self.wordList:
            wordlength = len(word)
            for charPosition in range(wordlength):
                for nextCharPos in [ i for i in range(self.minPartLength+charPosition,self.depth+self.minPartLength+charPosition) if charPosition+self.minPartLength < wordlength]:
                    try:
                        newPart = str(word[charPosition:nextCharPos])
                        nextChar = str(word[nextCharPos])
                        try:
                            self.wordPartToCharCounts[newPart][nextChar] += 1
                        except KeyError as key:
                            key = str(key)[1:-1]
                            if key == newPart:
                                self.wordPartList.append(newPart)
                                self.wordPartToCharCounts[newPart] = {nextChar:1}
                            elif key == nextChar:
                                self.wordPartToCharCounts[newPart][nextChar] = 1
                    except IndexError:
                        pass

    def prepareWeightVector(self):
        self.createWordPartList()
        for wordPart in self.wordPartList:
            if wordPart not in self.weightVector:
                self.weightVector[wordPart] = {char:0 for char in self.letters}

    def resetWeightVector(self):
        self.wordPartList = []
        self.wordPartToCharCounts = {}
        self.weightVector = {}
        self.createWordPartList()
        for wordPart in self.wordPartList:
            self.weightVector[wordPart] = {char:0 for char in self.letters}

    def createWeightVector(self,source, remindFile = False, depth = 3, minPartLength = 1, epsilon = 1):
        self.depth = depth
        self.minPartLength = minPartLength
        self.epsilon = epsilon
        print ("\nCreating the weight Vector ...")
        startTime = time.time()
        self.openText(source)     # Wortliste einlesen
        self.cleanText()
        if remindFile:
            self.prepareWeightVector()
        else:
            self.resetWeightVector()
        # Gewichtungsanpassung
        for wordPart in self.wordPartList:
            factor = len(wordPart)*self.epsilon
            for char in self.wordPartToCharCounts[wordPart]:
                counts = self.wordPartToCharCounts[wordPart][char]
                self.weightVector[wordPart][char] += self.increment * counts * factor
        self.cleanWeightVector()
        #print(self.weightVector)
        print ('Analysis took %.2f seconds' %(time.time()-startTime))

    def cleanWeightVector(self):
        # Bereinigen des weigtVectors
        ROUNDED_DIGITS = 2
        for wordPart in self.weightVector:
            for char in self.weightVector[wordPart]:
                if self.weightVector[wordPart][char] < 0:
                    self.weightVector[wordPart][char] = 0
                elif self.weightVector[wordPart][char] > self.limit and self.limit != 0:
                    self.weightVector[wordPart][char] = self.limit
                else:
                    self.weightVector[wordPart][char] = round(self.weightVector[wordPart][char],ROUNDED_DIGITS)

    def cleanText(self):
        for wordNumber in range(len(self.wordList)):
            for char in self.wordList[wordNumber]:
                if self.letters.find(char) == -1:
                    if char == 'ä':
                        self.wordList[wordNumber] = self.wordList[wordNumber].replace(char,'ae')
                    elif char == 'ö':
                        self.wordList[wordNumber] = self.wordList[wordNumber].replace(char,'oe')
                    elif char == 'ü':
                        self.wordList[wordNumber] = self.wordList[wordNumber].replace(char,'ue')
                    elif char == 'ß':
                        self.wordList[wordNumber] = self.wordList[wordNumber].replace(char,'ss')
                    else:
                        self.wordList[wordNumber] = self.wordList[wordNumber].replace(char,'')
            self.wordList[wordNumber] = self.wordList[wordNumber].lower()
        for emptyWord in [emptyWord for emptyWord in self.wordList if emptyWord == '']:
            self.wordList.remove(emptyWord)

    def openText(self,source): #hiermit wird ein Text eingelesen
        self.wordList = []
        try:
            with codecs.open(source,'r',encoding='utf-8') as file:
                for line in file.readlines():
                    line = line.lower()
                    wordsInLine = line.split()
                    for word in wordsInLine:
                        self.wordList.append(word)
        except UnicodeDecodeError:
            with open(source,'r') as file:
                for line in file.readlines():
                    line = line.lower()
                    wordsInLine = line.split()
                    for word in wordsInLine:
                        self.wordList.append(word)


    def printWeightVector(self):
        for wordPart in self.weightVector:
            print ("%s: \n %s" %(wordPart, self.weightVector[wordPart]))

    def getDigitsOfBiggestValue(self):
        startTime = time.time()
        numberList = []
        for wordPart in self.weightVector:
            for char in self.weightVector[wordPart]:
                numberList.append(self.weightVector[wordPart][char])
        print (('Getting digits of biggest value took %.2f seconds') %(time.time()-startTime))
        return len(str(round(max(numberList))))

    def saveWeightVector(self):
        startTime = time.time()
        max(self.weightVector)
        digits = self.getDigitsOfBiggestValue()
        saveFile = open ('weightVector.txt','w+')
        for wordPart in sorted(self.weightVector):
            line = wordPart + '{ '
            for char in sorted(self.weightVector[wordPart]):
                line += str(('%+1s:%-*.0f ') %(char,digits,self.weightVector[wordPart][char]))
            saveFile.write ( line + '}\n')
        saveFile.close()
        print (('Saving took %.2f seconds') %(time.time()-startTime))

    def pickleDateiWriter(self,saveFile,daten):
        saveFile.truncate (0)
        saveFile.write ( pickle.dumps(daten))
        saveFile.close()

LEARNING_SOURCE = 'Faust_I.txt'
MIN_LENGTH = 1
DEPTH = 3
EPSILON = 1/35
LIMIT = 10**6
REMEMBER = False

def main():
    """
    Einstiegspunkt
    """
    learner = LearningModule(LIMIT)
    learner.createWeightVector(LEARNING_SOURCE, REMEMBER, DEPTH, MIN_LENGTH)
    learner.saveWeightVector()
    #learner.printWeightVector()


if __name__ == "__main__":
    main()