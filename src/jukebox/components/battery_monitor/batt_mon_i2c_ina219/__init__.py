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
from ina219 import INA219
from ina219 import DeviceRangeError
from components.battery_monitor import BatteryMonitorBase

logger = logging.getLogger('jb.battmon')

batt_mon = None


class battmon_ina219(BatteryMonitorBase.BattmonBase):
    '''Battery Monitor based on a INA219

    CAUTION - WARNING
    ========================================================================
    Lithium and other batteries are dangerous and must be treated with care.
    Rechargeable Lithium Ion batteries are potentially hazardous and can
    present a serious FIRE HAZARD if damaged, defective or improperly used.
    Do not use this circuit to a lithium ion battery without expertise and
    training in handling and use of batteries of this type.
    Use appropriate test equipment and safety protocols during development.

    There is no warranty, this may not work as expected or at all!
    =========================================================================

    This script is intended to read out the Voltage of a single Cell LiIon Battery using a board with a INA219:

                                                  3.3V
                                                   +
                                                   |
                                              .----o----.
                                              |         |  SDA
              .-------------------------------o AIN     o------
              |                               | INA219  |  SCL
              |                    .----------o AOUT    o------
             ---                   |          |         |
     Battery  -           Regulator + Raspi   '----o----'
     2.9V-4.2V|                    |               |
              |                    |               |
             ===                  ===             ===

    '''

    def __init__(self, cfg):
        super().__init__(cfg, logger)

    def init_batt_mon_hw(self, num, denom):
        self.adc = INA219(float(num)/1000, busnum=1)
        self.adc.configure(self.adc.RANGE_16V, self.adc.GAIN_AUTO, self.adc.ADC_32SAMP, self.adc.ADC_32SAMP)

    def get_batt_voltage(self):
        batt_voltage_mV = self.adc.supply_voltage() * 1000.0
        return int(batt_voltage_mV)


@plugs.finalize
def finalize():
    global batt_mon
    cfg = jukebox.cfghandler.get_handler('jukebox')
    batt_mon = battmon_ina219(cfg)
    plugs.register(batt_mon, name='batt_mon')


@plugs.atexit
def atexit(**ignored_kwargs):
    global batt_mon
    batt_mon.status_thread.cancel()
