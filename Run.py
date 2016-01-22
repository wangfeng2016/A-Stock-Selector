'''
Created on Jan, 13, 2016

@author: Hanjie
'''

from utils.pathtools import *
from dataSpider import *
import traceback 
import os.path
import requests;
import struct
import pandas
import json

''' 
Usage: call this function to download history data csv file from yahoo for specified stock code
Input parameter: e.g. sz000001 or ss600000
'''
def downloadHistoryQuoteFile(code, debug=False, http_proxy=""):
    historyQuoteUrl = "http://table.finance.yahoo.com/table.csv?s=" + code[2:8] + "." + code[0:2] 
    if debug:
        print(historyQuoteUrl)
    localFilename = code[2:8] + ".csv"
    if debug:
        print("creating " + localFilename)
    if http_proxy<>"":  
        proxy = {}
        proxy['http'] = http_proxy         
    r = requests.get(historyQuoteUrl, stream=True, proxies=proxy)
    with open("./"+localFilename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: 
                f.write(chunk)
                f.flush()
        f.close()
    return localFilename

''' 
Usage: call this function to calculate the Moving Average: MA and append the value to the data csv file from yahoo for specified stock code
Input parameter: e.g. sz000001 or ss600000
'''
def calculateMA(code):
    fileName = convertOsPath(os.path.join(dataSpiderConfig._configDic['basePath'], (str(code) + '.csv')))
    if os.path.exists(fileName):
        stock_data = pandas.read_csv(fileName, parse_dates=[1])
        stock_data.sort('Date', inplace=True)
        ListMA = [5, 10, 20, 60]
        for ma in ListMA:
            stock_data['MA_' + str(ma)] = pandas.rolling_mean(stock_data['Close'], ma)
            stock_data.sort('Date', ascending=False, inplace=True)
            stock_data.to_csv('./sh600000_ma.csv', index=False)
    else:
        print (fileName + " does not exist, exiting")
        sys.exit()
    

'''
 Usage: call this function to read all stock code from TDX software, and write to stockCode.csv
 Input parameter: the directory where the TDX is installed
'''
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

if __name__ == '__main__':
    if(not os.path.exists("./conf.ini")):
        print("Conf.int file is missing, exiting...")
        exit
    else:
        print ("Start to read the configuration file from ./conf.ini ...")
        dataSpiderConfig = dataSpider("conf.ini")
        if dataSpiderConfig._configDic['debugMode']:
            print(dataSpiderConfig._configDic)
            
        stockCode = os.path.join(dataSpiderConfig._configDic['basePath'], 'dataRepository', 'stockCode.csv')
        if os.path.exists(stockCode):
            print("The default stockCod file exists as ", stockCode)  
        else:
            tdxRoot = os.path.join(dataSpiderConfig._configDic['basePath'], 'tdxRoot')
            if dataSpiderConfig._configDic['debugMode']:
                print(tdxRoot)
            if os.path.exists(tdxRoot):
                print("creating the stockCode file as ", stockCode)
                readStockCodeFromTDX(tdxRoot)
            else: 
                print('tdxRoot does not exist, which is mandatory here. exiting...')
                sys.exit()
        headers = ['code', 'name']
        stockInfo = pandas.read_csv(stockCode, header=None, names=headers)
        for code in stockInfo.code:
            fileName = convertOsPath(os.path.join(dataSpiderConfig._configDic['basePath'], (str(code) + '.csv')))
            print (fileName)
            if not os.path.exists(fileName):
                downloadHistoryQuoteFile("ss"+str(code), False, dataSpiderConfig._configDic['http_proxy'])
            calculateMA(code)
            sys.exit()    
          
        
       
