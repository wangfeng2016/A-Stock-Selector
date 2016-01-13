'''
Utility functions for local directory handling.
'''

from __future__ import print_function, unicode_literals
import sys
if sys.version_info[0] >= 3:
    from io import FileIO as BUILTIN_FILE_TYPE
    decodePath = lambda path: path
else:
    BUILTIN_FILE_TYPE = file
    import locale
    _PATH_ENCODING = locale.getpreferredencoding()
    decodePath = lambda path: path.decode(_PATH_ENCODING)

import os
import errno
import shutil
import stat
import tempfile


def ensureDir(path):
    '''Make sure that the provided path exists.'''
    # this implementation should be the most robust with regard to race conditions,
    # see http://stackoverflow.com/questions/273192/python-best-way-to-create-directory-if-it-doesnt-exist-for-file-write
    try:
        os.makedirs(path)
    except OSError as osError:
        if osError.errno != errno.EEXIST:
            raise


def ensureCleanDir(path):
    '''
    Make sure that the provided path exists and is clean.

    If the path already exists then all its content is deleted.
    '''
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=False, onerror=_handleRemoveReadonly)
        os.mkdir(path)
    else:
        os.makedirs(path)


def delDir(path):
    '''Delete the specified directory and all its content.'''
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=False, onerror=_handleRemoveReadonly)


def copyTree(sourcePath, targetPath, clean=False, ignore='*.svn*'):
    '''Copy all content of the specified path to the target path.

    :param clean: If True the target path is wiped before the copy operation.
    :param ignore: Provide an ignore pattern string
        (in the ``shutil.ignore_patterns`` format).
    '''
    if clean and os.path.exists(targetPath):
        shutil.rmtree(targetPath, ignore_errors=False,
                                          onerror=_handleRemoveReadonly)
    shutil.copytree(sourcePath, targetPath,
                    ignore=shutil.ignore_patterns(ignore))


def _handleRemoveReadonly(func, path, exc):
    '''Error handler to delete files that are read-only.'''
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def mkdtempUnicode():
    '''
    Return a temporary directory path created with tempfile.mkdtemp().

    The uncicode conversion is relevant for Python 2.x.

    On Windows systems it is additionally guaranteed that the path is provided
    in full length (without any 8 character short versions) and with the
    original capitalization.
    '''
    temppath = decodePath(tempfile.mkdtemp())
    return temppath

def mkstempUnicode():
    '''
    Return a temporary file (created with tempfile.NamedTemporaryFile) along
    with its path.
    
    See :func:`mkdTempUnicode` for more information.
    '''
    tempFile = tempfile.NamedTemporaryFile(delete=False)
    tempFilePath = decodePath(tempFile.name)
    return tempFile, tempFilePath

def convertOsPath(path):
    '''
    Convert OS-dependent relative path to the format of the current OS.

    Convert relative paths from Unix to Windows style and vice versa.
    Then, '~' or '~user' is expanded to the corresponding home directory.
    If an absolute windows path is given on a Unix system or the other way
    round, an error is raised.
    '''
    if '/' in path and os.sep == '\\':  # unix path on windows
        if path[0] == '/':
            raise Exception('Specified absolute Unix path on Windows.')
        newPath = path.replace('/', '\\')
    elif '\\' in path and os.sep == '/':    # windows path on unix
        if path[1:3] in [':\\', ':/']:
            raise Exception('Specified absolute Windows path on Unix.')
        newPath = path.replace('\\', '/')
    else:
        newPath = path
    return os.path.expanduser(newPath)