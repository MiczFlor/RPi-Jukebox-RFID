# Battery Monitor

> [!CAUTION]
> Lithium and other batteries are dangerous and must be treated with care.
> Rechargeable Lithium Ion batteries are potentially hazardous and can
> present a serious **FIRE HAZARD** if damaged, defective, or improperly used.
> Do not use this circuit for a lithium-ion battery without the expertise and
> training in handling and using batteries of this type.
> Use appropriate test equipment and safety protocols during development.
> There is no warranty, this may not work as expected!

## Battery Monitor based on a ADS1015

The script in [src/jukebox/components/battery_monitor/batt_mon_i2c_ads1015/\_\_init\_\_.py](../../../../src/jukebox/components/battery_monitor/batt_mon_i2c_ads1015/__init__.py) is intended to read out the voltage of a single Cell LiIon Battery using a [CY-ADS1015 Board](https://www.adafruit.com/product/1083):

```text
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
```

> [!WARNING]
>
> * the circuit is constantly draining the battery! (leak current up to: 2.1µA)
> * the time between sample needs to be a minimum 1sec with this high impedance voltage divider don't use the continuous conversion method!

## Battery Monitor based on an INA219

The script in [src/jukebox/components/battery_monitor/batt_mon_i2c_ina219/\_\_init\_\_.py](../../../../src/jukebox/components/battery_monitor/batt_mon_i2c_ina219/__init__.py) is intended to read out the voltage of a single cell or multiple LiIon Battery using a [INA219 Board](https://www.adafruit.com/product/904):

```text
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
```

## Configuration example

The battery monitoring is configured in the jukebox.yml file.

The "battmon" module has to be added to the modules setting.

```yaml
modules:
  named:
    # Do not change the order!
    publishing: publishing
    ...
    battmon: battery_monitor.batt_mon_i2c_ina219
```

The battmon module needs further configuration:

```yaml
battmon:
  scale_to_phy_num: 1
  scale_to_phy_denom: 0
  warning_action:
  all_clear_action:
```

The setting "scale_to_phy_denom" does not influence the INA219. However, the scale can be adjusted to fit multiple LiIon cells.
