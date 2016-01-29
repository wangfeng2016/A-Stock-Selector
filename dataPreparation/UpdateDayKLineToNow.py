import pandas
import re
from utils.pathtools import *
import datetime
import shutil 



class data(object):
    '''
    '''
    def __init__(self, fileName, debug=False):
        '''
        '''
        self.fileName = fileName
        self.now = datetime.datetime.now()
        self.debug = debug
        
    def dataUpdatedToWhichDay(self):
        data = pandas.read_csv(self.fileName, parse_dates=['Date'])
        data.sort_values(by='Date', inplace=True)
        lastUpdateToWhichDay = data.tail(1).loc[0].get_value('Date')
        return lastUpdateToWhichDay
        
    def categoryDataToFolderByUpdateDay(self):
        updatedToWhichDay = self.dataUpdatedToWhichDay().strftime("%Y%m%d")
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
        d.categoryDataToFolderByUpdateDay()
        