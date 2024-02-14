# MIT License
#
# Copyright (c) 2021 Arne Pagel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Contributing author(s):
# - Arne Pagel

import logging
import jukebox.plugs as plugs
import jukebox.cfghandler
import Adafruit_ADS1x15
from components.battery_monitor import BatteryMonitorBase

logger = logging.getLogger('jb.battmon')

batt_mon = None


class battmon_ads1015(BatteryMonitorBase.BattmonBase):
    """Battery Monitor based on a ADS1015

    See [Battery Monitor documentation](../../builders/components/power/batterymonitor.md)
    """

    def __init__(self, cfg):
        super().__init__(cfg, logger)

    def init_batt_mon_hw(self, num, denom):
        self.adc = Adafruit_ADS1x15.ADS1015()
        self.scale_to_phy = num / denom

    def get_batt_voltage(self):
        batt_voltage_mV_raw = self.adc.read_adc(0, gain=2)
        return int(batt_voltage_mV_raw * self.scale_to_phy)


@plugs.finalize
def finalize():
    global batt_mon
    cfg = jukebox.cfghandler.get_handler('jukebox')
    batt_mon = battmon_ads1015(cfg)
    plugs.register(batt_mon, name='batt_mon')


@plugs.atexit
def atexit(**ignored_kwargs):
    global batt_mon
    batt_mon.status_thread.cancel()
