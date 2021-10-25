#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, datetime

class Main:
    def __init__(self):
        self.nummer = 1

    def converter(self, outputFile, prettyLyrics):
        prettyLyrics = prettyLyrics.split('\n')
        ncontent = ""
        del prettyLyrics[0]
        for this in prettyLyrics:
            # print("THIS: "+this)
            huh = 0
            contento = this.split(' <')
            thhisLen = len(contento)-1
            wordNum = -1
            # print("CONTENTO: ", contento)
            for word in contento:
                # print("WORD: "+word)
                wordNum += 1
                if wordNum != thhisLen:
                    nextw = contento[wordNum+1]
                    nextw = nextw.replace("[", "")
                    nextw = nextw.replace("]", "$")
                    nextw = nextw.replace(">", "$")
                word = word.replace("[", "")
                word = word.replace("]", "$")
                word = word.replace(">", "$")

                begin = "00:"+word.split("$")[0].replace(".", ",")
                # print("BEGIN: "+begin)

                # lasttime = tnummer
                if wordNum == thhisLen:
                    self.cWord = '%s#' % word.split('$')[-1]
                    end = "00:"+prettyLyrics[huh+1].split(" <")[0].replace("[", "").replace("]", "$").split("$")[0].replace(".", ",")
                else:
                    self.cWord = word.split('$')[-1]
                    end = "00:"+nextw.split("$")[0].replace(".", ",")
                
                # print("CWORD: "+self.cWord)
                # print("END: "+end)

                ncontent = ncontent+'%s\n' % str(self.nummer)
                ncontent = ncontent+'%s --> %s\n' % (begin, end)
                ncontent = ncontent+'%s\n\n' % self.cWord
                self.nummer += 1
                if "#" in self.cWord:
                    break
            huh += 1
        nfile = open(outputFile, "w+")
        nfile.write(ncontent)
        nfile.close()

iFile = sys.argv[1]
oFile = sys.argv[2]
f = open(iFile, "r")
lyr = f.read()
f.close()
lyr = lyr.split('\n')
del lyr[0:4]
del lyr[-1]
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
lyrics = lyrics.replace("  ", " ").replace("\n\n", "\n").replace(" \n", "\n").replace("-", " ")

Main().converter(oFile, lyrics)