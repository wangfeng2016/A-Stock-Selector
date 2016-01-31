"""
"""
import pandas
import re
from utils.pathtools import *

class tortoise(object):
    '''
    '''
    def __init__(self, fileName, debug=False):
        '''
        '''
        self.fileName = fileName
        self.debug = debug
        
    def MaxIndays(self, N1):
        data = pandas.read_csv(self.fileName, parse_dates=['Date'])
        data = data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
        data.sort_values(by='Date', inplace=True)
        data_N1=data.tail(N1)
        if self.debug:
            print(data_N1[["Date", "High"]])
        return max(data_N1['High'])
    
    def MinIndays(self, N2):
        data = pandas.read_csv(self.fileName, parse_dates=['Date'])
        data = data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
        data.sort_values(by='Date', inplace=True)
        data_N2=data.tail(N2)
        if self.debug:
            print(data_N2[["Date", "Low"]])
        return min(data_N2['Low'])

if __name__ == '__main__':
    repository= convertOsPath(os.path.join('../', 'dataRepository'))
    print(repository)
    if not os.path.exists(repository):
        print("the repository does not exist, existing")
        sys.exit()
    re.compile("^[0-9]+\.csv$")    
    stockFiles=[]
    for root, dirs, files in os.walk(repository):
        for f in files:
            if re.compile("^[0-9]+.csv$").match(f):
                stockFiles.append(os.path.join(root,f))
    for stockFile in stockFiles:
        stock=tortoise(stockFile, True)
        print(stock.MaxIndays(20))
        print(stock.MinIndays(10))

