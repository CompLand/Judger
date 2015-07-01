#! /bin/python3
__author__ = 'Amir Khazaie 733amir@gmail.com'

import subprocess as sp


compilercommand = {
    'c': 'gcc',
    'c++': 'g++',
    'java': 'javac'
}
defaultarguments = {
    'gcc': [],
    'g++': [],
    'javac': []
}
outputarguments = {
    'gcc': '-o',
    'g++': '-o',
    'javac': '-d'
}


class Compiler:

    def __init__(self, language, compilerarguments, pathtosource, pathforexe):
        self.setcommand(language, compilerarguments, pathtosource, pathforexe)
        self.compile()

    def setcommand(self, lan, comarg, srcpath, exepath):
        self.command = [compilercommand[lan]] + (comarg and comarg or defaultarguments[compilercommand[lan]])
        self.command += [outputarguments[compilercommand[lan]], exepath]
        self.command += [srcpath]

    def compile(self):
        compilerprocess = sp.Popen(self.command, stdout=sp.PIPE, stderr=sp.PIPE)
        self.error = compilerprocess.communicate()[1].decode()

    def status(self):
        if self.error:
            return self.error
        return None
