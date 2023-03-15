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

import jukebox.plugs as plugs
import jukebox.cfghandler
import jukebox.publishing
import jukebox.multitimer as multitimer
import jukebox.utils as utils

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


class BattmonBase():
    '''Battery Monitor base class '''

    def __init__(self, cfg, logger):
        self._logger = logger
        self.batt_status = {}
        self.batt_status['soc'] = 0
        self.batt_status['charging'] = 0
        self.batt_status['voltage'] = 0
        self.interval = 5
        num = cfg.setndefault('battmon', 'scale_to_phy_num', value=35)
        denom = cfg.setndefault('battmon', 'scale_to_phy_denom', value=15)

        self.init_batt_mon_hw(num, denom)

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
        batt_voltage_mV = self.get_batt_voltage()

        self.f1 = pt1_frac(0.5, batt_voltage_mV)
        self.fs = pt1_frac(0.01, batt_voltage_mV)

        self.warning_action = cfg.setndefault('battmon', 'warning_action', value=None)
        self.all_clear_action = cfg.setndefault('battmon', 'all_clear_action', value=None)

        self.status_thread = multitimer.GenericEndlessTimerClass('batt_mon.timer_status', self.interval, self.publish_status)
        self.status_thread.start()

    def init_batt_mon_hw(self, num, denom):
        self._logger.error("init_batt_mon_hw shall be overwritten")

    def get_batt_voltage(self):
        self._logger.error("get_batt_voltage shall be overwritten")

    @plugs.tag
    def get_batt_status(self):
        return (self.batt_status)

    def publish_status(self):
        batt_voltage_mV_raw = self.get_batt_voltage()

        batt_voltage_mV = self.f1.iter(batt_voltage_mV_raw)
        batt_voltage_mV_slow = self.fs.iter(batt_voltage_mV_raw)

        soc = int(interpolate(self.soc_cc, batt_voltage_mV))

        if (batt_voltage_mV - batt_voltage_mV_slow) < 0:
            charging = 0
        else:
            charging = 1

        if (batt_voltage_mV < self.shutdown_voltage):
            self._logger.warning(f"Shutdown due to low Battery: {soc}%, Batt Voltage: {batt_voltage_mV}mV")
            plugs.call_ignore_errors('host', 'shutdown')

        if (batt_voltage_mV < self.warning_voltage):
            if (self.warning_action is not None):
                utils.decode_and_call_rpc_command(self.warning_action, self._logger)
        elif batt_voltage_mV > self.ok_voltage:
            if (self.all_clear_action is not None):
                utils.decode_and_call_rpc_command(self.all_clear_action, self._logger)

        self._logger.info(f"SOC: {soc}%, Batt Voltage: {batt_voltage_mV}mV, charging:{charging}")

        self.batt_status['soc'] = soc
        self.batt_status['charging'] = charging
        self.batt_status['voltage'] = batt_voltage_mV

        jukebox.publishing.get_publisher().send('batt_status', self.batt_status)
