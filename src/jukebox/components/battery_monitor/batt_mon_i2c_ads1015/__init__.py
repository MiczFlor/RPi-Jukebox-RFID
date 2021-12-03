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
    '''Battery Monitor based on a ADS1015

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

    This script is intended to read out the Voltage of a single Cell LiIon Battery using a CY-ADS1015 Board:

                                                  3.3V
                                                   +
                                                   |
                                              .----o----.
                        ___                   |         |  SDA
              .--------|___|---o----o---------o AIN0    o------
              |         2MΩ    |    |         |         |  SCL
              |               .-.   |         | ADS1015 o------
             ---              | |  ---        |         |
     Battery  -          1.5MΩ| |  ---100nF   '----o----'
     2.9V-4.2V|               '-'   |              |
              |                |    |              |
             ===              ===  ===            ===

    Attention:
        - the circuit is constantly draining the battery! (leak current up to: 2.1µA)
        - the time between sample needs to be a minimum 1sec with this high impedance voltage divider
          don't use the continuous conversion method!

    '''

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
