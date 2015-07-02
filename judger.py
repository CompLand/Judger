#! /bin/python3
__author__ = 'Amir Khazaie 733amir@gmail.com'

supportedlanguages = ['c', 'c++', 'java']
filteringcategories = ['acm']

import argparse
import os
import json
import tempfile
from shutil import copy
from compiler import Compiler
from runner import Runner

languageextension = {
    'c': '.c',
    'c++': '.cpp',
    'java': '.java'
}


class InputArgumentsError(RuntimeError):
    pass


class Judger:

    def set(self, language, timelimit, memorylimit, inputpath, outputpath, resultpath, diffargs, comargs, forcat, sourcepath, test):
        self.language = language
        self.timelimit = timelimit
        self.memorylimit = memorylimit
        self.inputpath = inputpath
        self.outputpath = outputpath
        self.resultpath = resultpath
        self.diffargs = diffargs
        self.comargs = comargs
        self.forcat = forcat
        self.sourcepath = sourcepath
        self.test = test
        self.checkargs()
        self.memorylimit = self.memorylimit * 1024 * 1024

    def handlecommnadlineargument(self):
        parser = argparse.ArgumentParser(description='This python script is auto-judging codes.', add_help=True)
        parser.add_argument('-v', '--version', action='version', version='Version Pre-alpha')
        parser.add_argument('-l', '--language', dest='language', help='language of source you want to be judged (lowercase)', choices=(supportedlanguages))
        parser.add_argument('-t', '--time-limit', type=int, dest='timelimit', help='time limit for the code (integer of seconds)')
        parser.add_argument('-m', '--memory-limit', type=int, dest='memorylimit', help='memory limit for the code (integer of MB)')
        parser.add_argument('-i', '--input-path', dest='inputpath', help='relative or absolute path to input file')
        parser.add_argument('-o', '--output-path', dest='outputpath', help='relative or absolute path to output file')
        parser.add_argument('-r', '--result-path',  dest='resultpath', help='relative or absolute path containing the name of result file')
        parser.add_argument('-d', '--diff-args', dest='diffargs', help='diff options to compare (put them in double quotes)')
        parser.add_argument('-c', '--compiler-args', dest='comargs', help='compiler options (put them in double quotes)')
        parser.add_argument('-f', '--forbidden-syntax', dest='forcat', help='select a category for checking forbidden syntaxes', choices=(filteringcategories))
        parser.add_argument(dest='sourcepath', help='relative or absolute path to source file')
        parser.add_argument('-test', action='store_true', dest='test', help='run complete test on whole project')
        parser.parse_args(namespace=self)
        self.checkargs()
        self.memorylimit = self.memorylimit * 1024 * 1024

    def checkargs(self):
        error = ''
        if self.language not in supportedlanguages:
            error = 'Language not supported.'
        elif type(self.timelimit) is not int:
            error = 'Time limit is not integer.'
        elif type(self.memorylimit) is not int:
            error = 'Memory limit is not integer.'
        elif not os.path.isfile(self.inputpath):
            error = 'Input path not pointing to a file.'
        elif not os.access(self.inputpath, os.R_OK):
            error = 'Input file is not readable.'
        elif not os.path.isfile(self.outputpath):
            error = 'Output path not pointing to a file.'
        elif not os.access(self.outputpath, os.R_OK):
            error = 'Output file is not readable.'
        elif not self.writable(self.resultpath):
            error = 'Can\'t write result file.'
        elif not self.forcat in filteringcategories:
            error = 'No category named \'%s\'.' % self.forcat
        elif not os.path.isfile(self.sourcepath):
            error = 'Source path not pointing to a file.'
        elif not os.access(self.sourcepath, os.R_OK):
            error = 'Source file is not readable.'
        if error:
            raise InputArgumentsError(error)

    def writable(self, path):
        try:
            f = open(path, 'w')
        except IOError:
            return False
        f.close()
        return True

    def judge(self):
        self.copyfiles()
        compiler = Compiler(self.language, [], self.sourcepath, self.exepath)
        if compiler.status():
            self.writeresultfile(self.resultpath, 'CE', compiler.status(), 0, 0)
            return None
        else:
            print("Compiled succesfully.")
        self.programoutput = 'programoutput'
        runner = Runner(self.timelimit, self.memorylimit, self.inputpath, os.path.join(self.tempdir.name, self.programoutput), self.exepath)
        f = open(os.path.join(self.tempdir.name, self.programoutput), 'r')
        print(f.read())

    def copyfiles(self):
        self.tempdir = tempfile.TemporaryDirectory()
        copy(self.inputpath, os.path.join(self.tempdir.name, 'input'))
        self.inputpath = os.path.join(self.tempdir.name, 'input')
        copy(self.outputpath, os.path.join(self.tempdir.name, 'output'))
        self.outputpath = os.path.join(self.tempdir.name, 'output')
        copy(self.sourcepath, os.path.join(self.tempdir.name, 'source' + languageextension[self.language]))
        self.sourcepath = os.path.join(self.tempdir.name, 'source' + languageextension[self.language])
        self.exepath = os.path.join(self.tempdir.name, 'exe')

    def writeresultfile(self, resultpath, status, error, time, memory):
        data = {
            'status': status,
            'error': error,
            'time': time,
            'memory': memory
        }
        with open(resultpath, 'w') as fp:
            json.dump(data, fp)


if __name__ == '__main__':
    j = Judger()
    j.handlecommnadlineargument()
    j.judge()
