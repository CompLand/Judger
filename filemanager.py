#! /bin/python
__author__ = 'Amir Khazaie 733amir@gmail.com'

from defaults import *
from os import path, makedirs
from shutil import copyfile, rmtree

class FileManager:
    def __init__(self, data):
        self.data = data
        self.destPath = path.join(absoluteDirPath(__file__), tempDirName)
        if not path.exists(self.destPath):
            makedirs(self.destPath)
        self.copyAll()
        self.data.update({source: self.tempSourcePath() , programInput: self.tempInputPath(), programOuput: self.tempOutputPath()})

    def srcExt(self):
        if self.data[sourceLanguage] == 'c':
            return '.c'
        elif self.data[sourceLanguage] in ['c++', 'cpp']:
            return '.cpp'
        elif self.data[sourceLanguage] == 'java':
            return '.java'

    def copyInput(self):
        copyfile(self.data[programInput], self.tempInputPath())

    def tempInputPath(self):
        return path.join(self.destPath, tempInputFile)

    def copyOutput(self):
        copyfile(self.data[programOuput], self.tempOutputPath())

    def tempOutputPath(self):
        return path.join(self.destPath, tempOutputFile)

    def copySource(self):
        copyfile(self.data[source], self.tempSourcePath())

    def tempSourcePath(self):
        return path.join(self.destPath, tempSourceFile) + self.srcExt()

    def copyAll(self):
        self.copyInput()
        self.copyOutput()
        self.copySource()

    def tempDirPath(self):
        return self.destPath
    def newPaths(self):
        return self.data

    def removeTempDir(self):
        rmtree(self.destPath)
