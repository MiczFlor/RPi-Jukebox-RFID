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
    '''battery monitor using the ads1015
    attention, the time between sample needs be be as minimum 1sec when a high impedance voltage divider is used.
    don't use the continious conversion mehtod!!!
    '''

    def __init__(self):
        self._logger = logger
        self.batt_status = {}
        self.batt_status['soc'] = 0
        self.batt_status['chargeing'] = 0
        self.batt_status['voltage'] = 0

        self.adc = Adafruit_ADS1x15.ADS1015()

        self.soc_cc = {3000: 0,
                       3200: 5,
                       3500: 20,
                       3900: 90,
                       4000: 95,
                       4200: 100}

        self.warning_voltage = 3300
        self.shutdown_voltage = 3000

        batt_voltage_mV_raw = self.adc.read_adc(0, gain=2)

        self.f1 = pt1_frac(0.5, batt_voltage_mV_raw)
        self.fs = pt1_frac(0.01, batt_voltage_mV_raw)

        self.warning_action = None
        self.all_clear_action = None

        self.status_thread = multitimer.GenericEndlessTimerClass('batt_mon.timer_status', 10, self.publish_status)
        self.status_thread.start()

    @plugs.register
    def get_batt_status(self):
        return(self.batt_status)

    def publish_status(self):
        batt_voltage_mV_raw = self.adc.read_adc(0, gain=2)

        batt_voltage_mV = self.f1.iter(batt_voltage_mV_raw)
        batt_voltage_mV_slow = self.f2.iter(batt_voltage_mV_raw)

        soc = interpolate(self.soc_cc, batt_voltage_mV)

        if (batt_voltage_mV - batt_voltage_mV_slow) > 0:
            chargeing = 1
        else:
            chargeing = 0

        if (batt_voltage_mV < self.shutdown_voltage):
            utils.decode_and_call_rpc_command("shutdown", self._logger)

        if (batt_voltage_mV < self.warning_voltage):
            if (self.warning_action is not None):
                utils.decode_and_call_rpc_command(self.warning_action, self._logger)
        else:
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
    batt_mon = battmon()

    plugs.register(batt_mon, name='batt_mon')


@plugs.atexit
def atexit(**ignored_kwargs):
    global batt_mon
    batt_mon.status_thread.cancel()
