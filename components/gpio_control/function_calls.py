import logging
import sys
from subprocess import check_call

logger = logging.getLogger(__name__)

playout_control = "../../scripts/playout_controls.sh "

def functionCallShutdown(*args):
    check_call("{command}-c=shutdown".format(command=playout_control), shell=True)


def functionCallVolU(steps=None):
    if steps is None:
        check_call("{command}-c=volumeup".format(command=playout_control), shell=True)
    else:
        check_call("{command}-c=volumeup -v={steps}".format(steps=steps,
            command=playout_control),
                shell=True)


def functionCallVolD(steps=None):
    if steps is None:
        check_call("{command}-c=volumedown".format(command=playout_control), shell=True)
    else:
        check_call("{command}-c=volumedown -v={steps}".format(steps=steps,
            command=playout_control),
                shell=True)


def functionCallVol0(*args):
    check_call("{command}-c=mute".format(command=playout_control), shell=True)


def functionCallPlayerNext(*args):
    check_call("{command}-c=playernext".format(command=playout_control), shell=True)


def functionCallPlayerPrev(*args):
    check_call("{command}-c=playerprev".format(command=playout_control), shell=True)


def functionCallPlayerPauseForce(*args):
    check_call("{command}-c=playerpauseforce".format(command=playout_control), shell=True)


def functionCallPlayerPause(*args):
    check_call("{command}-c=playerpause".format(command=playout_control), shell=True)


def functionCallRecordStart(*args):
    check_call("{command}-c=recordstart".format(command=playout_control), shell=True)


def functionCallRecordStop(*args):
    check_call("{command}-c=recordstop".format(command=playout_control), shell=True)


def functionCallRecordPlayLatest(*args):
    check_call("{command}-c=recordplaylatest".format(command=playout_control), shell=True)


def functionCallToggleWifi(*args):
    check_call("{command}-c=togglewifi".format(command=playout_control), shell=True)



def getFunctionCall(functionName):
    logger.error('Get FunctionCall: {} {}'.format(functionName,functionName in locals()))
    getattr(sys.modules[__name__], str)
    return locals().get(functionName, None)

