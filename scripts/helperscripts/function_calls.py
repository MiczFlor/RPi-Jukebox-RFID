import logging
import sys
from subprocess import check_call

logger = logging.getLogger(__name__)

def functionCallShutdown():
    check_call("./scripts/playout_controls.sh -c=shutdown", shell=True)


def functionCallVolU(steps=None):
    if steps is None:
        check_call("./scripts/playout_controls.sh -c=volumeup", shell=True)
    else:
        check_call("./scripts/playout_controls.sh -c=volumeup -v={steps}".format(steps), shell=True)


def functionCallVolD(steps=None):
    if steps is None:
        check_call("./scripts/playout_controls.sh -c=volumedown", shell=True)
    else:
        check_call("./scripts/playout_controls.sh -c=volumedown -v={steps}".format(steps), shell=True)


def functionCallVol0():
    check_call("./scripts/playout_controls.sh -c=mute", shell=True)


def functionCallPlayerNext():
    check_call("./scripts/playout_controls.sh -c=playernext", shell=True)


def functionCallPlayerPrev():
    check_call("./scripts/playout_controls.sh -c=playerprev", shell=True)


def functionCallPlayerPauseForce():
    check_call("./scripts/playout_controls.sh -c=playerpauseforce", shell=True)


def functionCallPlayerPause():
    check_call("./scripts/playout_controls.sh -c=playerpause", shell=True)


def functionCallRecordStart():
    check_call("./scripts/playout_controls.sh -c=recordstart", shell=True)


def functionCallRecordStop():
    check_call("./scripts/playout_controls.sh -c=recordstop", shell=True)


def functionCallRecordPlayLatest():
    check_call("./scripts/playout_controls.sh -c=recordplaylatest", shell=True)


def functionCallToggleWifi():
    check_call("./scripts/playout_controls.sh -c=togglewifi", shell=True)



def getFunctionCall(functionName):
    logger.error(f'Get FunctionCall: {functionName} {functionName in locals()}')
    getattr(sys.modules[__name__], str)
    return locals().get(functionName, None)

