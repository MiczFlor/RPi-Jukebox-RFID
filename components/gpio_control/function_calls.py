import logging
import sys
from subprocess import Popen as function_call
import os
import pathlib



currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
print (parentdir)

sys.path.append(parentdir+"/scripts")

print(sys.path)

from phonie_access_objects import phoniebox_object_access_queue


logger = logging.getLogger(__name__)

playout_control_relative_path = "../../scripts/playout_controls.sh"
function_calls_absolute_path = str(pathlib.Path(__file__).parent.absolute())
playout_control = os.path.abspath(os.path.join(function_calls_absolute_path, playout_control_relative_path))

def functionCallShutdown(*args):
    function_call("{command} -c=shutdown".format(command=playout_control), shell=True)


def functionCallVolU(steps=None):
    queue = phoniebox_object_access_queue()
    queue.connect()
    resp = queue.phonie_enqueue({'obj':'volume','cmd':'inc','param':None})
    
    #if steps is None:
    #    function_call("{command} -c=volumeup".format(command=playout_control), shell=True)
    #else:
    #    function_call("{command} -c=volumeup -v={steps}".format(steps=steps,
    #        command=playout_control),
    #            shell=True)


def functionCallVolD(steps=None):
    queue = phoniebox_object_access_queue()
    queue.connect()
    resp = queue.phonie_enqueue({'obj':'volume','cmd':'dec','param':None})
    
    #if steps is None:
    #    function_call("{command} -c=volumedown".format(command=playout_control), shell=True)
    #else:
    #    function_call("{command} -c=volumedown -v={steps}".format(steps=steps,
    #        command=playout_control),
    #            shell=True)


def functionCallVol0(*args):
    function_call("{command} -c=mute".format(command=playout_control), shell=True)


def functionCallPlayerNext(*args):
    function_call("{command} -c=playernext".format(command=playout_control), shell=True)


def functionCallPlayerPrev(*args):
    function_call("{command} -c=playerprev".format(command=playout_control), shell=True)


def functionCallPlayerPauseForce(*args):
    function_call("{command} -c=playerpauseforce".format(command=playout_control), shell=True)


def functionCallPlayerPause(*args):
    function_call("{command} -c=playerpause".format(command=playout_control), shell=True)


def functionCallRecordStart(*args):
    function_call("{command} -c=recordstart".format(command=playout_control), shell=True)


def functionCallRecordStop(*args):
    function_call("{command} -c=recordstop".format(command=playout_control), shell=True)


def functionCallRecordPlayLatest(*args):
    function_call("{command} -c=recordplaylatest".format(command=playout_control), shell=True)


def functionCallToggleWifi(*args):
    function_call("{command} -c=togglewifi".format(command=playout_control), shell=True)


def functionCallPlayerStop(*args):
    function_call("{command} -c=playerstop".format(command=playout_control),
            shell=True)


def functionCallPlayerSeekFwd(*args):
    function_call("{command} -c=playerseek -v=+10".format(command=playout_control), shell=True)


def functionCallPlayerSeekBack(*args):
    function_call("{command} -c=playerseek -v=-10".format(command=playout_control), shell=True)


def getFunctionCall(functionName):
    logger.error('Get FunctionCall: {} {}'.format(functionName, functionName in locals()))
    getattr(sys.modules[__name__], str)
    return locals().get(functionName, None)

