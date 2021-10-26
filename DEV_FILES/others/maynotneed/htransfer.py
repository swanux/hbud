#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse
import shutil
import json

# import cProfile
# import pstats

class Transser:

    def reset(self):
        global filePer
        global allSize
        global currPer
        global notVir
        global yetFil
        yetFil = ""
        filePer = 0
        allSize = 0
        currPer = 0
        notVir = False

    def yes_or_no(self, question, typ):
        if jsonmode == True:
            print(json.dumps({"string": question, "type": 'question'}))
            reply = str(input())
        else:
            reply = str(input(question+' (y/n/r/R): ')).strip()
        if reply[0] == 'y':
            if typ == 'spec':
                os.remove('{0}{1}'.format(dst, self.filenam))
            elif typ == 'merge':
                self.merge = True
            elif typ == 'specfile':
                os.remove(self.destt)
            else:
                os.remove(dst)
        elif reply[0] == 'R':
            if typ == 'spec':
                self.filenam = reply.split('/')[1]
            elif typ == 'specfile':
                splitt = self.destt.split('/')
                splitt[-1] = reply.split('/')[1]
                self.destt = '/'.join(splitt)
            else:
                self.repFil = True
                splitt = dst.split('/')
                splitt[-1] = reply.split('/')[1]
                self.nfile = '/'.join(splitt)
                print('############## 2')
                print(dst)
                self.canpass = True
        elif reply[0] == 'r':
            if typ == 'spec':
                try:
                    suffix = self.filenam.split('.')[-1]
                except:
                    suffix = ''
                if suffix == None or suffix == '':
                    self.filenam = reply.split('/')[1]
                else:
                    self.filenam = reply.split('/')[1]+'.'+suffix
            elif typ == 'specfile':
                splitt = self.destt.split('/')
                try:
                    suffix = splitt[-1].split('.')[-1]
                except:
                    suffix = ''
                if suffix == None or suffix == '':
                    splitt[-1] = reply.split('/')[1]
                else:
                    splitt[-1] = reply.split('/')[1]+'.'+suffix
                self.destt = '/'.join(splitt)
            else:
                # try:
                #     suffix = self.filenam.split('.')[-1]
                # except:
                #     suffix = ''
                # if suffix == None or suffix == '':
                #     self.filenam = reply.split(' ')[1]
                # else:
                #     self.filenam = reply.split(' ')[1]+'.'+suffix
                self.repFil = True
                splitt = dst.split('/')
                splitt[-1] = reply.split('/')[1]
                self.nfile = '/'.join(splitt)
                print('############## 2')
                print(dst)
                self.canpass = True
                # raise SystemExit
        elif reply[0] == 'n':
            print('Skip')
            self.skip = True
            self.canpass = True
        else:
            return self.yes_or_no("Invalid selection! : ", typ)

    def main(self, src, dst, start1):
        global currPer
        self.repFil = False
        self.merge = False
        self.canpass = False
        self.skip = False
        '''
        Copy a large file showing progress.
        '''
        src = src.replace('\ ', ' ')
        dst = dst.replace('\ ', ' ')
        if os.path.isfile(src):
            self.filenam = src.split('/')[-1]
        else:
            self.filenam = ''
        if os.path.exists(src) is False:
            if jsonmode == True:
                print(json.dumps({"string": 'ERROR: source does not exist: "{}"'.format(src), "type": 'error'}))
            else:
                print('ERROR: source does not exist: "{}"'.format(src))
            sys.exit(1)
        if os.path.exists(dst) is True:
            if os.path.isdir(dst):
                if dst.split('/')[-1] == None or dst.split('/')[-1] == "":
                    self.canpass = True
                    if os.path.isfile('{0}{1}'.format(dst, self.filenam)):
                        self.yes_or_no('Destination directory already contains file with this name {0}{1}! Would you like to continue and replace it or use another name?'.format(dst, self.filenam), 'spec')
                else:
                    if os.path.isdir(src):
                        splitt = src.split('/')
                        for i in range(len(splitt)):
                            if splitt[i] == "" and i != 0 or splitt[i] == None and i != 0:
                                break
                            else:
                                justDir = splitt[i]
                        self.yes_or_no('Destination directory {0}/{1} already exist. Would you like to merge them?'.format(dst, justDir), 'merge')
                        self.canpass = True
                    else:
                        if supportOverride == True:
                            print('Removing directory...')
                            shutil.rmtree(dst, ignore_errors=True)
                            print('Done')
                        else:
                            if jsonmode == True:
                                print(json.dumps({"string": 'ERROR: target directory exists, cannot overwrite it: "{}"'.format(dst), "type": 'error'}))
                            else:
                                print('ERROR: target directory exists, cannot overwrite it: "{}"'.format(dst))
                            self.skip = True
                            self.canpass = True
            else:
                if os.path.isdir(src):
                    self.yes_or_no('Destination file {} already exist! Would you like to continue and replace it or use another name?'.format(dst), 'file')
                else:
                    self.canpass = True
        if os.path.exists(dst) is True and self.canpass != True:
            if jsonmode == True:
                print(json.dumps({"string": 'ERROR: file exists, cannot overwrite it: "{}"'.format(dst), "type": 'error'}))
            else:
                print('ERROR: file exists, cannot overwrite it: "{}"'.format(dst))
            sys.exit(1)
        if jsonmode == True:
            pass
        else:
            self.UP = '\x1b[1A'
            self.DEL = '\x1b[2K'
        if self.skip == True:
            print('Skipping...')
        else:
            try:
                if os.path.isdir(src):
                    splitt = src.split('/')
                    for i in range(len(splitt)):
                        if splitt[i] == "" and i != 0 or splitt[i] == None and i != 0:
                            break
                        else:
                            justDir = splitt[i]
                    for (dirpath, dirnames, filenames) in os.walk(src):
                        dirList = dirpath.split('/')
                        newDirList = []
                        for i in range(len(dirList)):
                            if dirList[i] != justDir:
                                if dirList[i] == None or dirList[i] == "":
                                    pass
                                else:
                                    newDirList.append('/%s' % dirList[i])
                        for filename in filenames:
                            f = os.path.join(dirpath, filename)
                            specList = '/'.join(dirList)
                            specList = specList[specList.find(justDir):].replace('{}/'.format(justDir), '')
                            try:
                                relPath = dirpath.replace(''.join(newDirList), "")
                                relPath = relPath.replace(' ', '\ ')
                                relPath = relPath.replace("'", "\\'")
                                relPath = relPath[relPath.replace("\ ", "-").find(justDir.replace(" ", "-")):]
                                if self.repFil == True:
                                    dst = self.nfile
                                dst = dst.replace(' ', '\ ')
                                # print(dst, justDir, relPath, specList)
                                if dst.split('/')[-1] == None or dst.split('/')[-1] == "":
                                    os.system('mkdir -p %s%s' % (dst, relPath))
                                else:
                                    if self.merge == True:
                                        os.system('mkdir -p %s/%s/%s' % (dst, justDir, specList))
                                    else:
                                        os.system('mkdir -p %s/%s' % (dst, relPath))
                                dst = dst.replace('\ ', ' ')
                            except:
                                pass
                            relPath = relPath.replace("\\'", "'")
                            relPath = relPath.replace('\ ', ' ')
                            # print('#####################')
                            # print(relPath, newDirList, justDir, dirList, filename, specList)
                            # print('#####################')
                            if self.repFil == True:
                                filename = self.nfile
                                self.repFil = False
                            if dst.split('/')[-1] == None or dst.split('/')[-1] == "":
                                tmpthing = '%s%s/%s' % (dst, relPath, filename)
                                self.calcs(f, 10000, tmpthing.replace('//', '/'), allSize, currPer)
                            else:
                                if self.merge == True:
                                    if newDirList != []:
                                        self.calcs(f, 10000, '%s/%s/%s/%s' % (dst, justDir, specList, filename), allSize, currPer)
                                    else:
                                        self.calcs(f, 10000, '%s/%s' % (dst, filename), allSize, currPer)
                                else:
                                    self.calcs(f, 10000, '%s/%s/%s' % (dst, relPath, filename), allSize, currPer)
                    if mv == True:
                        shutil.rmtree(src, ignore_errors=True)
                else:
                    # splitt = src.split('/')
                    # for i in range(len(splitt)):
                    #     if splitt[i] == "" and i != 0 or splitt[i] == None and i != 0:
                    #         break
                    #     else:
                    #         justFil = splitt[i]
                    justFil = self.filenam
                    if dst.split('/')[-1] == None or dst.split('/')[-1] == "":
                        self.calcs(src, 10000, '%s%s' % (dst, justFil), allSize, currPer)
                    else:
                        self.calcs(src, 10000, dst, allSize, currPer)
                    if mv == True:
                        os.remove(src)
            except IOError as obj:
                if jsonmode == True:
                    print(json.dumps({"string": 'ERROR: {}'.format(obj), "type": 'error'}))
                else:
                    print('ERROR: {}'.format(obj))
                sys.exit(1)


    def oneFile(self, fullSize, lastPer):
        global filePer
        global notVir
        global currPer
        self.copied = 0  # bytes
        self.chunk = self.ifp.read(int(self.chunk_size+1))
        while self.chunk:
            if self.skip == False:
                # Write and calculate how much has been written so far.
                self.ofp.write(self.chunk)
                self.copied += len(self.chunk)
                per = 100. * float(self.copied) / float(self.size)
                if fullSize != 0:
                    allPer = 100. * float(self.copied) / float(fullSize) + lastPer
                # Calculate the speed.
                elapsed = time.time() - self.start  # elapsed so far
                avg_byte_per_time = float(self.copied) / elapsed
                # avg_mbyte_per_time = avg_byte_per_time / (1024*1024)
                if __name__ == '__main__':
                    if jsonmode == True:
                        pass
                    else:
                        sys.stdout.write(self.UP + self.UP + self.DEL + 'Speed: %s B/s\n\n' % avg_byte_per_time)
                # Write out the status.
                if __name__ == '__main__':
                    if fullSize != 0:
                        if jsonmode == True:
                            jprog = allPer
                        else:
                            sys.stdout.write(self.UP + self.DEL + 'Progress: %s %%\n' % allPer)
                    else:
                        if jsonmode == True:
                            jprog = per
                        else:
                            sys.stdout.write(self.UP + self.DEL + 'Progress: %s %%\n' % per)
                # Calculate the estimated time remaining.
                avg_time_per_byte = elapsed / float(self.copied)
                if fullSize != 0:
                    fullCopied = (fullSize / 100) * allPer
                    remaining = fullSize - fullCopied
                else:
                    remaining = self.size - self.copied
                est = remaining * avg_time_per_byte
                if __name__ == '__main__':
                    if jsonmode == True:
                        # print(time.time()-self.jtime)
                        if time.time()-self.jtime >= 0.15:
                            self.jtime = time.time()
                            print(json.dumps({"file" : self.jfi, "type" : "status", "eta" : est, "speed" : avg_byte_per_time, "progress" : jprog}))
                    else:
                        sys.stdout.write(self.DEL + 'ETA: %s s\r' % est)
                        sys.stdout.flush()
                    notVir = True
                # Read in the next chunk.
                self.chunk = self.ifp.read(int(self.chunk_size+1))
                filePer = per
                currPer = allPer
            else:
                print('else')
                self.skip = False
                self.copied = self.size
                per = 100
                if fullSize != 0:
                    allPer = 100. * float(self.copied) / float(fullSize) + lastPer
                filePer = per
                currPer = allPer

    def calcs(self, current, divisor, dest, fullSize=0, lastPer=0):
        global notVir
        global yetFil
        self.start = time.time()
        self.jtime = self.start
        self.size = os.stat(current).st_size
        if self.size >= 1000000:
            self.chunk_size = self.size / divisor
            while self.chunk_size == 0 and divisor > 10:
                divisor /= 10
                self.chunk_size = self.size / divisor
        else:
            self.chunk_size = 10000
        with open(current, 'rb') as self.ifp:
            if __name__ == '__main__':
                if jsonmode == True:
                    self.jfi = current
                else:
                    os.system('clear')
                    sys.stdout.write(self.DEL + 'Current file is %s\n\n\n' % current)
            yetFil = current
            self.destt = dest
            if os.path.exists(self.destt):
                if os.path.isdir(self.destt):
                    if supportOverride == True:
                        print('Removing directory...')
                        shutil.rmtree(dst, ignore_errors=True)
                        print('Done')
                    else:
                        if jsonmode == True:
                            print(json.dumps({"string": 'ERROR: target directory exists, cannot overwrite it: "{}"'.format(dst), "type": 'error'}))
                        else:
                            print('ERROR: target directory exists, cannot overwrite it: "{}"'.format(dst))
                        self.skip = True
                else:
                    self.yes_or_no('Destination file {} already exist! Would you like to continue and replace it or use another name?'.format(self.destt), 'specfile')
            try:
                with open(self.destt, 'wb') as self.ofp:
                    # profile = cProfile.Profile()
                    # profile.runcall(self.oneFile, fullSize, lastPer)
                    # ps = pstats.Stats(profile)
                    # ps.print_stats()
                    self.oneFile(fullSize, lastPer)
            except Exception as probl:
                if jsonmode == True:
                    print(json.dumps({"string": 'ERROR: {}'.format(probl), "type": 'error'}))
                else:
                    print('ERROR: {}'.format(probl))

    def modPre(self, modSr, modDs):
        global allSize
        dst = modDs
        src = modSr.split(', ')
        start1 = time.time()
        self.reset()
        if len(src) == 1:
            src = src[0]
            src = src.replace('\ ', ' ')
            if os.path.isdir(src):
                listOfFiles = list()
                for (dirpath, dirnames, filenames) in os.walk(src):
                    listOfFiles += [os.path.join(dirpath, file) for file in filenames]
                for i in listOfFiles:
                    allSize += os.stat(i).st_size
            else:
                allSize += os.stat(src).st_size
            self.main(src, dst, start1)
        elif len(src) >= 2:
            listOfFiles = list()
            for item in src:
                item = item.replace('\ ', ' ')
                if os.path.isdir(item):
                    for (dirpath, dirnames, filenames) in os.walk(item):
                        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
                    for i in listOfFiles:
                        allSize += os.stat(i).st_size
                else:
                    allSize += os.stat(item).st_size
            for item in src:
                self.main(item, dst, start1)

if __name__ == '__main__':
    arger = argparse.ArgumentParser(description='HTransfer: python recursive file transfer backend with status indication.\nDesigned for eXternOS, by swanux')
    group = arger.add_mutually_exclusive_group(required=True)

    group.add_argument("-mv", default=None, help="Move file/folder", action="store_true")
    group.add_argument("-cp", default=None, help="Copy file/folder", action="store_true")
    arger.add_argument("-src", "--source", default=None, help="Source folder/file", required=True)
    arger.add_argument("-dst", "--destination", default=None, help="Destination folder/file", required=True)
    arger.add_argument("-js", "--jsonmode", default=None, help="Json output mode", action="store_true")
    arger.add_argument("-so", "--supportOverride", default=None, help="Support overriding whole directory", action="store_true")

    args = arger.parse_args()
    mv = args.mv
    cp = args.cp
    src = args.source
    dst = args.destination
    src = src.split(', ')
    jsonmode = args.jsonmode
    supportOverride = args.supportOverride
    start1 = time.time()
    Transser().reset()
    if len(src) == 1:
        src = src[0]
        src = src.replace('\ ', ' ')
        if os.path.isdir(src):
            listOfFiles = list()
            for (dirpath, dirnames, filenames) in os.walk(src):
                listOfFiles += [os.path.join(dirpath, file) for file in filenames]
            for i in listOfFiles:
                allSize += os.stat(i).st_size
        else:
            allSize += os.stat(src).st_size
        # profile = cProfile.Profile()
        # profile.runcall(Transser().main, src, dst, start1)
        # ps = pstats.Stats(profile)
        # ps.print_stats()
        Transser().main(src, dst, start1)
    elif len(src) >= 2:
        listOfFiles = list()
        for item in src:
            item = item.replace('\ ', ' ')
            if os.path.isdir(item):
                for (dirpath, dirnames, filenames) in os.walk(item):
                    listOfFiles += [os.path.join(dirpath, file) for file in filenames]
                for i in listOfFiles:
                    allSize += os.stat(i).st_size
            else:
                allSize += os.stat(item).st_size
        for item in src:
            Transser().main(item, dst, start1)
    elapsed = time.time() - start1
    print('\ncopied everything in {:>.1f} s'.format(elapsed))
else:
    mv = False
    print('Module mode')