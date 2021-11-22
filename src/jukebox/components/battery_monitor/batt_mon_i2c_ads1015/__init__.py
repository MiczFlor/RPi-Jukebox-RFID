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
import jukebox.publishing
import jukebox.multitimer as multitimer
import jukebox.utils as utils
import Adafruit_ADS1x15

logger = logging.getLogger('jb.battmon')
# cfg = jukebox.cfghandler.get_handler('jukebox')

batt_mon = None


class pt1_frac():
    '''fixed point first order filter, fractional format: 2^16,2^16'''
    def __init__(self, coeff, init=0):
        self.coeff = int(65536 * coeff)
        self.store = int(init) << 16

    def iter(self, input):
        self.store = self.store + ((input - (self.store >> 16)) * self.coeff)
        return (self.store >> 16)


def interpolate(cc, input):
    key_list = list(cc.keys())
    next_key = key_list[-1]
    prev_key = key_list[0]

    if (input <= prev_key):
        y = cc[prev_key]
    elif (input >= next_key):
        y = cc[next_key]
    else:
        for key in key_list:
            if (key < input):
                prev_key = key
            else:
                next_key = key
                break

        prev_value = cc[prev_key]
        next_value = cc[next_key]

        # linear interpolation
        temp = ((input - prev_key) * (next_value - prev_value) / (next_key - prev_key))
        y = temp + prev_value

    return y


class battmon():
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
        self._logger = logger
        self.batt_status = {}
        self.batt_status['soc'] = 0
        self.batt_status['chargeing'] = 0
        self.batt_status['voltage'] = 0
        self.interval = 5
        self.scale_to_phy_num = cfg.setndefault('battmon', 'scale_to_phy_num', value=35)
        self.scale_to_phy_denom = cfg.setndefault('battmon', 'scale_to_phy_denom', value=15)
        self.scale_to_phy = self.scale_to_phy_num / self.scale_to_phy_denom

        self.adc = Adafruit_ADS1x15.ADS1015()

        self.soc_cc = {3000: 0,
                       3200: 5,
                       3500: 20,
                       3900: 90,
                       4000: 95,
                       4200: 100}

        self.ok_voltage = 3400
        self.warning_voltage = 3300
        self.shutdown_voltage = 3000

        self.last_sample_time = -5
        batt_voltage_mV = self.get_adc_scaled()

        self.f1 = pt1_frac(0.5, batt_voltage_mV)
        self.fs = pt1_frac(0.01, batt_voltage_mV)

        self.warning_action = cfg.setndefault('battmon', 'warning_action', value=None)
        self.all_clear_action = cfg.setndefault('battmon', 'all_clear_action', value=None)

        self.status_thread = multitimer.GenericEndlessTimerClass('batt_mon.timer_status', self.interval, self.publish_status)
        self.status_thread.start()

    def get_adc_scaled(self):
        batt_voltage_mV_raw = self.adc.read_adc(0, gain=2)
        return int(batt_voltage_mV_raw * self.scale_to_phy)

    @plugs.tag
    def get_batt_status(self):
        return(self.batt_status)

    def publish_status(self):
        batt_voltage_mV_raw = self.get_adc_scaled()

        batt_voltage_mV = self.f1.iter(batt_voltage_mV_raw)
        batt_voltage_mV_slow = self.fs.iter(batt_voltage_mV_raw)

        soc = int(interpolate(self.soc_cc, batt_voltage_mV))

        if (batt_voltage_mV - batt_voltage_mV_slow) < 0:
            chargeing = 0
        else:
            chargeing = 1

        if (batt_voltage_mV < self.shutdown_voltage):
            self._logger.warning(f"Shutdown due to low Battery: {soc}%, Batt Voltage: {batt_voltage_mV}mV")
            plugs.call_ignore_errors('host', 'shutdown')

        if (batt_voltage_mV < self.warning_voltage):
            if (self.warning_action is not None):
                utils.decode_and_call_rpc_command(self.warning_action, self._logger)
        elif batt_voltage_mV > self.ok_voltage:
            if (self.all_clear_action is not None):
                utils.decode_and_call_rpc_command(self.all_clear_action, self._logger)

        self._logger.info(f"SOC: {soc}%, Batt Voltage: {batt_voltage_mV}mV, charging:{chargeing}")

        self.batt_status['soc'] = soc
        self.batt_status['chargeing'] = chargeing
        self.batt_status['voltage'] = batt_voltage_mV

        jukebox.publishing.get_publisher().send('batt_status', self.batt_status)


@plugs.finalize
def finalize():
    global batt_mon
    cfg = jukebox.cfghandler.get_handler('jukebox')
    batt_mon = battmon(cfg)
    plugs.register(batt_mon, name='batt_mon')


@plugs.atexit
def atexit(**ignored_kwargs):
    global batt_mon
    batt_mon.status_thread.cancel()
