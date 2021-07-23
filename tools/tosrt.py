#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, datetime

class Main:
    def __init__(self):
        self.nummer = 1

    def converter(self, inputFile, outputFile, prettyLyrics):
        sfile = open(inputFile, "r")
        contento = sfile.read()
        sfile.close()
        contento = contento.replace('BREATH*', 'BREATH *')
        contento = contento.split('\n')
        del contento[-1]
        prettyLyrics = prettyLyrics.replace('\n\n', '\n')
        prettyLyrics = prettyLyrics.split('\n')
        ncontent = ""
        lasttime = -1
        for this in prettyLyrics:
            tnummer = 0
            thhisLen = len(this.split(' '))-1
            print(thhisLen)
            print(prettyLyrics)
            print(this)
            wordNum = -1
            for self.line in contento:
                if lasttime+1 == tnummer:
                    wordNum += 1
                    print(self.line)
                    linelist = self.line.split(' ')

                    prebegin = str(datetime.timedelta(seconds=float(linelist[0])))
                    if linelist[0].split('.')[1] == "0" or linelist[0].split('.')[1] == "00":
                        t = [prebegin.split('.')[0], "000000"]
                    else:
                        t = prebegin.split('.')
                    t1 = list(t[1])
                    for i in range(3):
                        del t1[-1]
                    prebegin = ""
                    for i in t1:
                        prebegin = prebegin+i
                    begin = '%s,%s' % (t[0], prebegin)

                    lasttime = tnummer
                    print(wordNum)
                    if wordNum == thhisLen:
                        self.cWord = '%s#' % this.split(' ')[wordNum]
                    else:
                        self.cWord = this.split(' ')[wordNum]

                    preend = str(datetime.timedelta(seconds=float(linelist[1])))
                    if linelist[1].split('.')[1] == "0" or linelist[1].split('.')[1] == "00":
                        t = [preend.split('.')[0], "000000"]
                    else:
                        t = preend.split('.')
                    t1 = list(t[1])
                    for i in range(3):
                        del t1[-1]
                    preend = ""
                    for i in t1:
                        preend = preend+i
                    end = '%s,%s' % (t[0], preend)
                    ncontent = ncontent+'%s\n' % str(self.nummer)
                    ncontent = ncontent+'%s --> %s\n' % (begin, end)
                    ncontent = ncontent+'%s\n\n' % self.cWord
                    self.nummer += 1
                    if "#" in self.cWord:
                        break
                else:
                    pass
                tnummer += 1
        nfile = open(outputFile, "w+")
        nfile.write(ncontent)
        nfile.close()

iFile = sys.argv[1]
oFile = sys.argv[3]
f = open(sys.argv[2], "r")
lyr = f.read()
f.close()
lyr = lyr.split('\n')
del lyr[-1]
lyrics = ""
lenn = len(lyr)-1
cnummer = 0
for i in lyr:
    if cnummer < lenn:
        lyrics = lyrics+'%s\n' % i
    else:
        lyrics = lyrics+'%s' % i
    cnummer +=1
lyrics = lyrics.replace("  ", " ").replace("\n\n", "\n").replace(" \n", "\n")

Main().converter(iFile, oFile, lyrics)
