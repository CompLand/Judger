#! /bin/python
__author__ = 'Amir Khazaie 733amir@gmail.com'

from defaults import *

class CAHandler:
    def __init__(self, CommandLineArguments):
        self.data = {}
        self._handleCommandLineArguments(CommandLineArguments)

    def _handleCommandLineArguments(self, cmdargs):
        for i in range(1, len(cmdargs)):
            if cmdargs[i] in languageArguments:
                self.data[sourceLanguage] = cmdargs[i + 1]
            elif cmdargs[i] in timeLimitArguments:
                self.data[timeLimit] = int(cmdargs[i + 1])
            elif cmdargs[i] in memoryLimitArguments:
                self.data[memoryLimit] = int(cmdargs[i + 1])
            elif cmdargs[i] in programInputArguments:
                self.data[programInput] = cmdargs[i + 1]
            elif cmdargs[i] in programOuputArguments:
                self.data[programOuput] = cmdargs[i + 1]
            elif cmdargs[i] in resultPathArguments:
                self.data[resultPath] = cmdargs[i + 1]
            elif cmdargs[i] in compareArguments:
                self.data[compare] = cmdargs[i + 1]
            elif cmdargs[i] in compilerArguments:
                self.data[compiler] = cmdargs[i + 1]
            elif cmdargs[i] in forbiddenSyntaxArguments:
                self.data[forbiddenSyntax] = True
            elif cmdargs[i] in sourceArguments:
                self.data[source] = cmdargs[i + 1]
        self._argumentsCheck()

    def _argumentsCheck(self):
        for arg in requiredArguments.keys():
            self.data[arg] = self.data.get(arg, requiredArguments[arg])

    def getCommandLineArguments(self):
        return self.data
