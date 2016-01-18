'''
dataSpider class for dealing with configuration file and its content.
'''

from __future__ import print_function, unicode_literals

_convertDictUnicode = lambda dictInst: dictInst

from ConfigParser import RawConfigParser

from utils.pathtools import *
import os
import logging
logger = logging.getLogger(__name__)

# TODO: add method to write a valid configuration template

class dataSpider(object):
    '''
    Class to manage the configuration of the dataSpider.

    It is also responsible to instantiate and provide implementations
    of analysis parts, based on the specified values in the configuration.
    '''

### Configuration File example###
    CONFIG_EXAMPLE = r'''
'''

    DATETIME_FORMAT = '{%Y-%m-%d %H:%M}'

    def __init__(self, filename, callDependencyInjector=False):
        '''Load and initialize the configuration from the given filename.'''
        self._configDic = self._readConfig(filename)
        self._configFilename = filename

    reportPath = property(lambda self: os.path.join(self._configDic['basePath'],
                                                    'reports'))
    repositoryPath = property(lambda self: os.path.join(self._configDic['basePath'],
                                                'repository'))
    cachePath = property(lambda self: os.path.join(self._configDic['basePath'],
                                                   'cache'))
    profilePath = property(lambda self: os.path.join(self._configDic['basePath'],
                                                     'profile'))
    logPath = property(lambda self: os.path.join(self._configDic['basePath'],
                                                 'log'))
    debugMode = property(lambda self: self._configDic['debugMode'])
    
   
    def getLoggerConfig(self):
        '''Return a dict with the configuration values for the logger.'''
        return {
            'debugMode': self.debugMode,
            'consoleLog': self._configDic['consoleLog'],
            'logPath': self.logPath
        }


    @classmethod
    def _readConfig(cls, filename):
        '''
        Read the configuration file and return a pythonic configuration dict.
        '''
        confParser = RawConfigParser(defaults={
            # these keys can be commented out in the config file,
            # warning: the values are converted to strings
            'user': None,
            'pathRegexFilter': '',
            'filenameRegexFilter': '',
            'subPath': '',
            'includes': '',
            'macros': '',
            'languages': '',
            'metrics': '',
            'settings': '',
            'aggregateIssueLinks': '',
            'shortBlockLines': 4}
        )
        parsedFiles = confParser.read(filename)
        if not parsedFiles:
            msg = "Configuration file {} could not be read.".format(filename)
            raise Exception(msg)
        conf = {
            'sina': {},
            'neteasy': {},
            'hanjie': {},
            'matching': {},
        }
        # TODO: The 'configfie' entry is unused
        conf['consoleLog'] = confParser.getboolean('global', 'consoleLog')
        conf['debugMode'] = confParser.getboolean('global', 'debugMode')
        conf['encoding'] = confParser.get('global', 'encoding')
        conf['configfile'] = os.path.abspath(filename)
        conf['basePath'] = os.path.abspath(convertOsPath(confParser.get('global', 'basePath')))
        if confParser.has_section('sina'):
           conf['sina']['url'] = confParser.get('sina', 'url')
           conf['sina']['user'] = confParser.get('sina','user')
           conf['sina']['password'] = confParser.get('sina','password')
        if confParser.has_section('netease'):
           conf['netease']['url'] = confParser.get('netease', 'url')
           conf['netease']['user'] = confParser.get('netease','user')
           conf['netease']['password'] = confParser.get('netease','password')
        
        _convertDictUnicode(conf)
        return conf

    @classmethod
    def writeTemplateFile(cls, filename):
        '''Create a template configuration file.'''
        with open(filename, 'wt', encoding='utf-8') as configFile:
            configFile.write(cls.CONFIG_EXAMPLE)
