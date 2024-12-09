# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder

import logging
import jukebox.plugs as plugs
import jukebox.cfghandler
from ina219 import INA219
from ina219 import DeviceRangeError
from components.battery_monitor import BatteryMonitorBase

logger = logging.getLogger('jb.battmon.ina219')

batt_mon = None


class battmon_ina219(BatteryMonitorBase.BattmonBase):
    '''Battery Monitor based on a INA219

    See [Battery Monitor documentation](../../builders/components/power/batterymonitor.md)
    '''

    def __init__(self, cfg):
        super().__init__(cfg, logger)

    def init_batt_mon_hw(self, num: float, denom: float) -> None:
        try:
            self.adc = INA219(float(num) / 1000, busnum=1)
            self.adc.configure(self.adc.RANGE_16V, self.adc.GAIN_AUTO, self.adc.ADC_32SAMP, self.adc.ADC_32SAMP)
        except DeviceRangeError as e:
            logger.error(f"Device range error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize INA219: {e}")
            raise

    def get_batt_voltage(self) -> int:
        try:
            batt_voltage_mV = self.adc.supply_voltage() * 1000.0
            return int(batt_voltage_mV)
        except Exception as e:
            logger.error(f"Failed to get supply voltage from INA219: {e}")
            raise


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
