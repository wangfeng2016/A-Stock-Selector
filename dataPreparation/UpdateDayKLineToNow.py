import pandas
import re
from utils.pathtools import *
import datetime
import shutil 
import requests
import urllib, urllib2
'''
http://quotes.money.163.com/service/chddata.html?code=0601398&start=20150508&end=20150508
'''
def downloadHistoryInPeriod(code, start, end):
    dataUrl = "http://quotes.money.163.com/service/chddata.html?code=0" + code + "&start=" + start + "&end=" + end  
    print dataUrl
    r = requests.get(dataUrl, stream=True)
    lines = r.content.decode('gb2312').split("\n")
    lines =lines[1:len(lines)-1] #delete the first and last line
    
    stockInfo_new = []
    for line in lines:
        stockInfo = line.split(",", 14)    
        sDate = stockInfo[0]
        sNumber = code
        sClose = stockInfo[3]
        sHigh = stockInfo[4]
        sLow = stockInfo[5]
        sOpen = stockInfo[6]
        sVolumn = stockInfo[11]
        newline = sDate + "," + sNumber + "," + sOpen + "," + sHigh + "," + sLow + "," + sClose  + "," + sVolumn 
        stockInfo_new.append(newline)
    return stockInfo_new
    
class data(object):
    '''
    '''
    def __init__(self, fileName, debug=False):
        '''
        '''
        self.fileName = fileName
        self.debug = debug
        
    def dataUpdatedToWhichDay(self):
        data = pandas.read_csv(self.fileName, parse_dates=['Date'])
        data.sort_values(by='Date', inplace=True)
        lastUpdateToWhichDay = data.tail(1).loc[0].get_value('Date')
        return lastUpdateToWhichDay.strftime("%Y%m%d")
        
    def categoryDataToFolderByUpdateDay(self, lastUpdateToWhichDay):
        updatedToWhichDay = lastUpdateToWhichDay
        folder = convertOsPath(os.path.join('../', 'dataRepository', updatedToWhichDay))
        dest = os.path.join(folder, (os.path.basename(stockFile)))
        if not os.path.exists(folder):
            os.mkdir(folder)
        if not os.path.exists(dest):
            print("Move " + stockFile + " To " + dest)
            shutil.move(stockFile,dest)
            
    
if __name__ == '__main__':
    repository= convertOsPath(os.path.join('../', 'dataRepository'))
    if not os.path.exists(repository):
        print("the repository does not exist, existing")
        sys.exit()
    re.compile("^[0-9]+\.csv$")    
    stockFiles=[]
    for f in os.listdir(repository):
        if re.compile("^[0-9]+.csv$").match(f) and os.path.isfile(os.path.join(repository,f)):
            stockFiles.append(os.path.join(repository,f))
    
    for stockFile in stockFiles:
        print(stockFile)
        d = data(stockFile)
        lastUpdateToWhichDay=d.dataUpdatedToWhichDay()
        d.categoryDataToFolderByUpdateDay(lastUpdateToWhichDay)
        start = (datetime.datetime.strptime(lastUpdateToWhichDay,'%Y%m%d') - datetime.timedelta(days=1)).strftime("%Y%m%d")
        end = datetime.date.today().strftime("%Y%m%d")
        print(start, end)
    downloadHistoryInPeriod("600000", start, end)    