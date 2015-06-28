#! /bin/python
__author__ = 'Amir Khazaie 733amir@gmail.com'

sourceLanguage = 'srclan'
languageArguments = ['-l', '--lang', '--language']
timeLimit = 'timelimit'
timeLimitArguments = ['-t', '--time', '--time-limit']
memoryLimit = 'memorylimit'
memoryLimitArguments = ['-m', '--memory', '--memory-limit']
programInput = 'proginput'
programInputArguments = ['-i', '--input', '--program-input']
programOuput = 'progoutput'
programOuputArguments = ['-o', '--output', '--program-output']
resultPath = 'respath'
resultPathArguments = ['-r', '--result', '--result-path']
compare = 'compare'
compareArguments = ['-d', '--diff-args', '--diff-arguments']
compiler = 'compiler'
compilerArguments = ['-c', '--compiler-arguments']
forbiddenSyntax = 'forbiddensyntax'
forbiddenSyntaxArguments = ['-f', '--forbidden-syntax']
source = 'source'
sourceArguments = ['-s', '--source']

requiredArguments = {sourceLanguage: 'c++', timeLimit: 3, memoryLimit: 0, programInput: 'file.in',
                     programOuput: 'file.out', resultPath: 'file.r', compare: '', compiler: '',
                     forbiddenSyntax: True, source: 'main.cpp'}

languageCompilerCommand = {
    'c++': 'g++',
    'cpp': 'g++',
    'c': 'gcc',
    'java': 'javac'
}
