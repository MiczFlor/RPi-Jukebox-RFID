import logging
import sys
from subprocess import Popen as function_call
import os
import pathlib

class phoniebox_function_calls:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        playout_control_relative_path = "../../scripts/playout_controls.sh"
        function_calls_absolute_path = str(pathlib.Path(__file__).parent.absolute())
        self.playout_control = os.path.abspath(os.path.join(function_calls_absolute_path, playout_control_relative_path))

    def functionCallShutdown(self,*args):
        function_call("{command} -c=shutdown".format(command=self.playout_control), shell=True)


    def functionCallVolU(self,steps=None):
        if steps is None:
            function_call("{command} -c=volumeup".format(command=self.playout_control), shell=True)
        else:
            function_call("{command} -c=volumeup -v={steps}".format(steps=steps,
                command=self.playout_control),
                    shell=True)


    def functionCallVolD(self,steps=None):
        if steps is None:
            function_call("{command} -c=volumedown".format(command=self.playout_control), shell=True)
        else:
            function_call("{command} -c=volumedown -v={steps}".format(steps=steps,
                command=self.playout_control),
                    shell=True)


    def functionCallVol0(self,*args):
        function_call("{command} -c=mute".format(command=self.playout_control), shell=True)


    def functionCallPlayerNext(self,*args):
        function_call("{command} -c=playernext".format(command=self.playout_control), shell=True)


    def functionCallPlayerPrev(self,*args):
        function_call("{command} -c=playerprev".format(command=self.playout_control), shell=True)


    def functionCallPlayerPauseForce(self,*args):
        function_call("{command} -c=playerpauseforce".format(command=self.playout_control), shell=True)


    def functionCallPlayerPause(self,*args):
        function_call("{command} -c=playerpause".format(command=self.playout_control), shell=True)


    def functionCallRecordStart(self,*args):
        function_call("{command} -c=recordstart".format(command=self.playout_control), shell=True)


    def functionCallRecordStop(self,*args):
        function_call("{command} -c=recordstop".format(command=self.playout_control), shell=True)


    def functionCallRecordPlayLatest(self,*args):
        function_call("{command} -c=recordplaylatest".format(command=self.playout_control), shell=True)


    def functionCallToggleWifi(self,*args):
        function_call("{command} -c=togglewifi".format(command=self.playout_control), shell=True)


    def functionCallPlayerStop(self,*args):
        function_call("{command} -c=playerstop".format(command=self.playout_control),
                shell=True)


    def functionCallPlayerSeekFwd(self,*args):
        function_call("{command} -c=playerseek -v=+10".format(command=self.playout_control), shell=True)


    def functionCallPlayerSeekBack(self,*args):
        function_call("{command} -c=playerseek -v=-10".format(command=self.playout_control), shell=True)


    def functionCallBluetoothToggle(self,*args):
        function_call("{command} -c=bluetoothtoggle -v=toggle".format(command=self.playout_control), shell=True)


    def getFunctionCall(self,functionName):
        self.logger.error('Get FunctionCall: {} {}'.format(functionName, functionName in locals()))
        getattr(sys.modules[__name__], str)
        return locals().get(functionName, None)

