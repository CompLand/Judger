#! /bin/python3
__author__ = 'Amir Khazaie 733amir@gmail.com'

import time
import subprocess as sp
import psutil

class RunnerError(RuntimeError):
    def __init__(self, args):
        self.args = args


class Runner:

    def __init__(self, timelimit, memorylimit, inputpath, outputpath, exepath):
        self.timelimit = timelimit
        self.memorylimit = memorylimit
        self.inputpath = inputpath
        self.outputpath = outputpath
        self.exepath = exepath
        self.run()

    def run(self):
        starttime = time.time()
        exe = sp.Popen(self.exepath, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        exe.stdin = bytes(open(self.inputpath, 'r').read(), 'ascii')
        p = psutil.Process(exe.pid)
        maximummemory = 0
        processtime = 0
        rssinfo = p.memory_info()[0]
        while processtime <= self.timelimit and 0 < rssinfo <= self.memorylimit:
                rssinfo = p.memory_info()[0]
                processtime = time.time() - starttime
                maximummemory = rssinfo if rssinfo > maximummemory else maximummemory
        self.maximummemory = maximummemory
        self.timeprocessexe = processtime
        if rssinfo != 0:
            p.kill()
            if processtime > self.timelimit:
                raise RunnerError(('TLE', maximummemory, processtime))
            elif rssinfo > self.memorylimit:
                print("Memory limit exceeded.")
                raise RunnerError(('MLE', maximummemory, processtime))
        else:
            output, error = exe.communicate()
            if error:
                raise RunnerError(('RE', maximummemory, processtime))
            else:
                open(self.outputpath, 'w').write(output.decode())
