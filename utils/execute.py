'''
Module to enable non-blocking IO handling with the ``subprocess`` module.
'''

from __future__ import print_function, unicode_literals

import subprocess
import threading
#import locale
import os
import logging
logger = logging.getLogger(__name__)

# Warning: Using sys.stdout.encoding seems to return inconsistent results and
#        can lead to a unicode decode error.
#        Using locale.getpreferredencoding() prevents UTF-8 from being parsed
#        since it is (wrongly) interpreted as whatever local encoding is set.
STD_ENCODING = "UTF-8"

# Fixing mixed encodings sometimes encountered in messages
# See http://stackoverflow.com/questions/10009753/python-dealing-with-mixed-encoding-files
import codecs
last_position = -1
last_string = None
def mixed_decoder(unicode_error):
    global last_position
    global last_string
    string = unicode_error.object
    if not string is last_string:
        last_position = -1
    last_string = string
    position = unicode_error.start
    if position <= last_position:
        position = last_position + 1
    last_position = position
    new_char = string[position:position+1].decode("latin-1")
    return new_char, position + 1
codecs.register_error("mixed", mixed_decoder)


class ExecuteException(Exception):
    '''Exception to signal an error for a subprocess command line execution.'''

    def __init__(self, commandStr, returnCode=None,
                 stdoutText=None, stderrText=None, 
                 excecptionToPack=None):
        self.commandStr = commandStr
        self.returnCode = returnCode
        self.stdoutText = stdoutText
        self.stderrText = stderrText
        self.packedException = excecptionToPack

    def __str__(self):
        msg = ('Error executing "{}"\nRETURN CODE: {}'.
               format(self.commandStr, self.returnCode))
        if self.stdoutText or self.stderrText:
            msg += ('\n  STDOUT: {}\n  STDERR: {}'.
                    format(self.stdoutText, self.stderrText))
        return msg


def noOutputExecute(cmd, path=None, **kwargs):
    '''
    Execute the given command list and discard all output.

    It simply checks the return code and raises an ExecuteException if it is
    not ``None``.
    '''
    logger.debug('execute command "' + ' '.join(cmd) + '"')
    devNull = open(os.devnull, 'w')
    try:
        returnCode = subprocess.call(cmd, cwd=path, stdout=devNull,
                                     stderr=devNull, **kwargs)
    except Exception as exception:
        msg = (' '.join(cmd) + '\noriginal Error message:\n' + str(exception))
        raise ExecuteException(msg)
    finally:
        devNull.close()
    if returnCode:
        raise ExecuteException(' '.join(cmd), returnCode)


def stdOutputExecute(cmd, path=None, accept_exitcode=(0,), **kwargs):
    '''
    Execute the given command list and return the stdout output.

    The stderr output is discarded.

    It returns the the unicode string of the stdout output.

    If the exit code is not in the accept_exitcode tuple, raises an
    ExecuteException
    '''
    logger.debug('execute command "' + ' '.join(cmd) + '"')
    devNull = open(os.devnull, 'w')
    try:
        if 'stderr' in kwargs: 
            # The conditional is added due to Altova defect 42745. To work
            # around this defect, stderr must be redirected to stdout when 
            # calling DiffDogBatch.exe via stdOutputExsecute. This cannot be done 
            # when in the call to subprocess.check_output stderr is hardwired to 
            # devNull (as in the call in the else-block). When 42745 is fixed, 
            # the conditionalcan be removed, so that instead of the if-else 
            # construct there is only the call in the else-block.
            output = subprocess.check_output(cmd, cwd=path, **kwargs)
        else:
            output = subprocess.check_output(cmd, cwd=path, stderr=devNull, **kwargs)
    except subprocess.CalledProcessError as exception:
        if exception.returncode in accept_exitcode:
            print("Warning: ", cmd, " exited with status ", 
                  exception.returncode, " (accepted)")
            output = exception.output
        else:
            msg = (' '.join(cmd) + '\noriginal Error message:\n'
                   + str(exception))
            raise ExecuteException(commandStr=msg,
                                   returnCode=exception.returncode, 
                                   excecptionToPack=exception)
    except Exception as exception:
        msg = (' '.join(cmd) + '\noriginal Error message:\n' + str(exception))
        raise ExecuteException(msg)
    finally:
        devNull.close()
    return output.decode(STD_ENCODING, "mixed")


def asyncOutputExecute(cmd, path=None, stdoutWrite=None, stderrWrite=None,
                       returnOutput=False, **kwargs):
    '''
    Execute the given command list and optionally return the output.

    This function can read the output from both stdout and stderr in
    real time and hand it to the provided write functions. This is useful
    for commands that take a very long time or that might wait for user
    input for some error cases (which one might otherwise never see).

    :param cmd: List of command components.
    :param path: Optional path string of the intended working directory (to
        override the current working directory).
    :param stdoutWrite: Function that takes a string argument, like the
        ``write`` method of a file. The function is called for each line of the
        process stdout.
    :param stderrWrite: Function that takes a string argument, like the
        ``write`` method of a file. The function is called for each line of the
        process stdout.
    :param returnOutput: If true then the output of stderr and stdout
        is returned as two lists of unicode line strings. The lines nomrally
        already    contain a line break at the end.
    :param kwargs: Keyword arguments that are forwarded to subprocess (e.g.,
        ``shell=True``).
    '''
    logger.debug('execute command "' + ' '.join(cmd) + '"')
    try:
        proc = subprocess.Popen(cmd, cwd=path, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, **kwargs)
    except Exception as exception:
        msg = (' '.join(cmd) + '\noriginal Error message:\n' + str(exception))
        raise ExecuteException(msg)
    if returnOutput:
        stdoutLines, stderrLines = [], []
    else:
        stdoutLines, stderrLines = None, None
    stdoutThread = _startReadThread(proc.stdout, lines=stdoutLines,
                                    writeFunc=stdoutWrite, name='stdoutRead')
    stderrThread = _startReadThread(proc.stderr, lines=stderrLines,
                                    writeFunc=stderrWrite, name='stderrRead')
    returnCode = proc.wait()
    stdoutThread.join()
    stderrThread.join()
    if not returnCode == 0:
        commandStr = ' '.join(cmd)
        if returnOutput:
            raise ExecuteException(commandStr, returnCode,
                                   ''.join(stdoutLines), ''.join(stderrLines))
        else:
            raise ExecuteException(commandStr, returnCode)
    if returnOutput:
        return stdoutLines, stderrLines
    else:
        return None


def _startReadThread(pipe, lines=None, writeFunc=None, name='readThread'):
    '''
    Start and return a thread that reads from the given pipe.

    :param lines: If a list instance is provided (with an ``append`` method)
        then the read lines are appended.
    :writeFunc: If a function is provided then it is called for each retrieved
        line (e.g., this could be ``sys.stdout.write`` to print the output in
        real time).
    '''
    def readFunc():
        while True:
            line = pipe.readline().decode(STD_ENCODING, "mixed")
            if not line:
                break
            if lines is not None:
                lines.append(line)
            if writeFunc:
                writeFunc(line)
    thread = threading.Thread(name=name, target=readFunc)
    thread.daemon = True
    thread.start()
    logger.debug("Active Threads: " + str(threading.active_count()))
    return thread
