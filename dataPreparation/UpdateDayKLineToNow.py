import pandas
import re
from utils.pathtools import *
import datetime



class data(object):
    '''
    '''
    def __init__(self, fileName, debug=False):
        '''
        '''
        self.fileName = fileName
        self.now = datetime.datetime.now()
        self.debug = debug
        
    def dataUpdatedToWhen(self):
        data = pandas.read_csv(self.fileName, parse_dates=['Date'])
        data = data[['Date']]
        data.sort_values(by='Date', inplace=True)
        
        lastUpdatedTo=data.tail(1).loc[0].get_value('Date')
        print(self.now.strftime("%Y-%m-%d"))
        print(lastUpdatedTo.strftime("%Y-%m-%d"))
        print(self.now - lastUpdatedTo)
        
        
    
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
        print(data(stockFile).dataUpdatedToWhen())
   
