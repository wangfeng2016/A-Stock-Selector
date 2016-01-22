# this file contains functions to download history quote data file
#
import requests;
import struct
import pandas
import os.path

# Usage: call this function to download history data csv file from yahoo for specified stock code
# Input parameter: e.g. sz000001 or ss600000
def downloadHistoryQuoteFile(code):
    historyQuoteUrl = "http://table.finance.yahoo.com/table.csv?s=" + code[2:8] + "." + code[0:2] 
    print historyQuoteUrl
    localFilename = code + ".csv"
    print localFilename
    r = requests.get(historyQuoteUrl, stream=True)
    with open("./"+localFilename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: 
                f.write(chunk)
                f.flush()
        f.close()
    return localFilename

# Usage: call this function to read all stock code from TDX software, and write to stockCode.csv
# Input parameter: the directory where the TDX is installed
def readStockCodeFromTDX(tdxDir):
    fo = open('.\stockCode.csv', 'wb');

    fi = open(tdxDir+'\T0002\hq_cache\shex.tnf','rb')
    fi.seek(50)
    ss = fi.read(250)
    while ss<>'':
        if ss[0] == '6':
            fo.write(ss[0:6])
            fo.write(',')
        if (ss[30]).encode('hex') == "00":
            fo.write(ss[24:30])
        elif (ss[31]).encode('hex') == "00":
            fo.write(ss[24:31])
        else:
            fo.write(ss[24:32])
            fo.write('\n')
        ss = fi.read(250)
    fi.close()

    fi = open(tdxDir+'\T0002\hq_cache\szex.tnf','rb')
    fi.seek(50)
    ss = fi.read(250)
    while ss<>'':
        if ss[0:2] == '00' or ss[0:3] == '300':
            fo.write(ss[0:6])
            fo.write(',')
        if (ss[30]).encode('hex') == "00":
            fo.write(ss[24:30])
        elif (ss[31]).encode('hex') == "00":
            fo.write(ss[24:31])
        else:
            fo.write(ss[24:32])
            fo.write('\n')
        ss = fi.read(250)
    fi.close()
    fo.close()

# test
#readStockCodeFromTDX("d:\zd_zszq")

headers = ['code', 'name']
stockInfo = pandas.read_csv('.\stockCode.csv', header=None, names=headers)
for code in stockInfo.code:
    downloadHistoryQuoteFile("ss"+str(code))
