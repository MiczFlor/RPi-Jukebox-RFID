# None

## Table of Contents

* [run\_jukebox](#run_jukebox)
* [run\_rpc\_tool](#run_rpc_tool)
  * [get\_common\_beginning](#run_rpc_tool.get_common_beginning)
  * [runcmd](#run_rpc_tool.runcmd)
* [run\_register\_rfid\_reader](#run_register_rfid_reader)
* [run\_publicity\_sniffer](#run_publicity_sniffer)
* [\_\_init\_\_](#__init__)
* [run\_configure\_audio](#run_configure_audio)
* [components](#components)
* [components.mqtt.utils](#components.mqtt.utils)
  * [play\_folder\_recursive\_args](#components.mqtt.utils.play_folder_recursive_args)
  * [parse\_repeat\_mode](#components.mqtt.utils.parse_repeat_mode)
  * [get\_args](#components.mqtt.utils.get_args)
  * [get\_rpc\_command](#components.mqtt.utils.get_rpc_command)
  * [get\_kwargs](#components.mqtt.utils.get_kwargs)
  * [get\_current\_time\_milli](#components.mqtt.utils.get_current_time_milli)
  * [split\_topic](#components.mqtt.utils.split_topic)
  * [map\_repeat\_mode](#components.mqtt.utils.map_repeat_mode)
* [components.mqtt.mqtt\_command\_alias](#components.mqtt.mqtt_command_alias)
  * [get\_mute](#components.mqtt.mqtt_command_alias.get_mute)
* [components.mqtt.mqtt\_const](#components.mqtt.mqtt_const)
* [components.mqtt](#components.mqtt)
  * [MQTT](#components.mqtt.MQTT)
    * [run](#components.mqtt.MQTT.run)
    * [stop](#components.mqtt.MQTT.stop)
  * [on\_connect](#components.mqtt.on_connect)
  * [initialize](#components.mqtt.initialize)
* [components.volume](#components.volume)
  * [PulseMonitor](#components.volume.PulseMonitor)
    * [SoundCardConnectCallbacks](#components.volume.PulseMonitor.SoundCardConnectCallbacks)
    * [toggle\_on\_connect](#components.volume.PulseMonitor.toggle_on_connect)
    * [toggle\_on\_connect](#components.volume.PulseMonitor.toggle_on_connect)
    * [stop](#components.volume.PulseMonitor.stop)
    * [run](#components.volume.PulseMonitor.run)
  * [PulseVolumeControl](#components.volume.PulseVolumeControl)
    * [OutputChangeCallbackHandler](#components.volume.PulseVolumeControl.OutputChangeCallbackHandler)
    * [OutputVolumeCallbackHandler](#components.volume.PulseVolumeControl.OutputVolumeCallbackHandler)
    * [toggle\_output](#components.volume.PulseVolumeControl.toggle_output)
    * [get\_outputs](#components.volume.PulseVolumeControl.get_outputs)
    * [publish\_volume](#components.volume.PulseVolumeControl.publish_volume)
    * [publish\_outputs](#components.volume.PulseVolumeControl.publish_outputs)
    * [set\_volume](#components.volume.PulseVolumeControl.set_volume)
    * [get\_volume](#components.volume.PulseVolumeControl.get_volume)
    * [change\_volume](#components.volume.PulseVolumeControl.change_volume)
    * [get\_mute](#components.volume.PulseVolumeControl.get_mute)
    * [mute](#components.volume.PulseVolumeControl.mute)
    * [set\_output](#components.volume.PulseVolumeControl.set_output)
    * [set\_soft\_max\_volume](#components.volume.PulseVolumeControl.set_soft_max_volume)
    * [get\_soft\_max\_volume](#components.volume.PulseVolumeControl.get_soft_max_volume)
    * [card\_list](#components.volume.PulseVolumeControl.card_list)
* [components.rpc\_command\_alias](#components.rpc_command_alias)
* [components.synchronisation](#components.synchronisation)
* [components.synchronisation.syncutils](#components.synchronisation.syncutils)
* [components.synchronisation.rfidcards](#components.synchronisation.rfidcards)
  * [SyncRfidcards](#components.synchronisation.rfidcards.SyncRfidcards)
    * [sync\_change\_on\_rfid\_scan](#components.synchronisation.rfidcards.SyncRfidcards.sync_change_on_rfid_scan)
    * [sync\_all](#components.synchronisation.rfidcards.SyncRfidcards.sync_all)
    * [sync\_card\_database](#components.synchronisation.rfidcards.SyncRfidcards.sync_card_database)
    * [sync\_folder](#components.synchronisation.rfidcards.SyncRfidcards.sync_folder)
* [components.jingle.jinglemp3](#components.jingle.jinglemp3)
  * [JingleMp3Play](#components.jingle.jinglemp3.JingleMp3Play)
    * [play](#components.jingle.jinglemp3.JingleMp3Play.play)
  * [JingleMp3PlayBuilder](#components.jingle.jinglemp3.JingleMp3PlayBuilder)
    * [\_\_init\_\_](#components.jingle.jinglemp3.JingleMp3PlayBuilder.__init__)
* [components.jingle](#components.jingle)
  * [JingleFactory](#components.jingle.JingleFactory)
    * [list](#components.jingle.JingleFactory.list)
  * [play](#components.jingle.play)
  * [play\_startup](#components.jingle.play_startup)
  * [play\_shutdown](#components.jingle.play_shutdown)
* [components.jingle.alsawave](#components.jingle.alsawave)
  * [AlsaWave](#components.jingle.alsawave.AlsaWave)
    * [play](#components.jingle.alsawave.AlsaWave.play)
  * [AlsaWaveBuilder](#components.jingle.alsawave.AlsaWaveBuilder)
    * [\_\_init\_\_](#components.jingle.alsawave.AlsaWaveBuilder.__init__)
* [components.hostif.linux](#components.hostif.linux)
  * [shutdown](#components.hostif.linux.shutdown)
  * [reboot](#components.hostif.linux.reboot)
  * [jukebox\_is\_service](#components.hostif.linux.jukebox_is_service)
  * [is\_any\_jukebox\_service\_active](#components.hostif.linux.is_any_jukebox_service_active)
  * [restart\_service](#components.hostif.linux.restart_service)
  * [get\_disk\_usage](#components.hostif.linux.get_disk_usage)
  * [get\_cpu\_temperature](#components.hostif.linux.get_cpu_temperature)
  * [get\_ip\_address](#components.hostif.linux.get_ip_address)
  * [wlan\_disable\_power\_down](#components.hostif.linux.wlan_disable_power_down)
  * [get\_autohotspot\_status](#components.hostif.linux.get_autohotspot_status)
  * [stop\_autohotspot](#components.hostif.linux.stop_autohotspot)
  * [start\_autohotspot](#components.hostif.linux.start_autohotspot)
* [components.timers](#components.timers)
* [components.playermpd.coverart\_cache\_manager](#components.playermpd.coverart_cache_manager)
* [components.playermpd.playcontentcallback](#components.playermpd.playcontentcallback)
  * [PlayContentCallbacks](#components.playermpd.playcontentcallback.PlayContentCallbacks)
    * [register](#components.playermpd.playcontentcallback.PlayContentCallbacks.register)
    * [run\_callbacks](#components.playermpd.playcontentcallback.PlayContentCallbacks.run_callbacks)
* [components.playermpd](#components.playermpd)
  * [PlayerMPD](#components.playermpd.PlayerMPD)
    * [mpd\_retry\_with\_mutex](#components.playermpd.PlayerMPD.mpd_retry_with_mutex)
    * [pause](#components.playermpd.PlayerMPD.pause)
    * [next](#components.playermpd.PlayerMPD.next)
    * [rewind](#components.playermpd.PlayerMPD.rewind)
    * [replay](#components.playermpd.PlayerMPD.replay)
    * [toggle](#components.playermpd.PlayerMPD.toggle)
    * [replay\_if\_stopped](#components.playermpd.PlayerMPD.replay_if_stopped)
    * [play\_card](#components.playermpd.PlayerMPD.play_card)
    * [flush\_coverart\_cache](#components.playermpd.PlayerMPD.flush_coverart_cache)
    * [get\_folder\_content](#components.playermpd.PlayerMPD.get_folder_content)
    * [play\_folder](#components.playermpd.PlayerMPD.play_folder)
    * [play\_album](#components.playermpd.PlayerMPD.play_album)
    * [get\_volume](#components.playermpd.PlayerMPD.get_volume)
    * [set\_volume](#components.playermpd.PlayerMPD.set_volume)
  * [play\_card\_callbacks](#components.playermpd.play_card_callbacks)
* [components.gpio.gpioz.core.converter](#components.gpio.gpioz.core.converter)
  * [ColorProperty](#components.gpio.gpioz.core.converter.ColorProperty)
  * [VolumeToRGB](#components.gpio.gpioz.core.converter.VolumeToRGB)
    * [\_\_call\_\_](#components.gpio.gpioz.core.converter.VolumeToRGB.__call__)
    * [luminize](#components.gpio.gpioz.core.converter.VolumeToRGB.luminize)
* [components.gpio.gpioz.core.mock](#components.gpio.gpioz.core.mock)
  * [patch\_mock\_outputs\_with\_callback](#components.gpio.gpioz.core.mock.patch_mock_outputs_with_callback)
* [components.gpio.gpioz.core.output\_devices](#components.gpio.gpioz.core.output_devices)
  * [LED](#components.gpio.gpioz.core.output_devices.LED)
    * [flash](#components.gpio.gpioz.core.output_devices.LED.flash)
  * [Buzzer](#components.gpio.gpioz.core.output_devices.Buzzer)
    * [flash](#components.gpio.gpioz.core.output_devices.Buzzer.flash)
  * [PWMLED](#components.gpio.gpioz.core.output_devices.PWMLED)
    * [flash](#components.gpio.gpioz.core.output_devices.PWMLED.flash)
  * [RGBLED](#components.gpio.gpioz.core.output_devices.RGBLED)
    * [flash](#components.gpio.gpioz.core.output_devices.RGBLED.flash)
  * [TonalBuzzer](#components.gpio.gpioz.core.output_devices.TonalBuzzer)
    * [flash](#components.gpio.gpioz.core.output_devices.TonalBuzzer.flash)
    * [melody](#components.gpio.gpioz.core.output_devices.TonalBuzzer.melody)
* [components.gpio.gpioz.core.input\_devices](#components.gpio.gpioz.core.input_devices)
  * [NameMixin](#components.gpio.gpioz.core.input_devices.NameMixin)
    * [set\_rpc\_actions](#components.gpio.gpioz.core.input_devices.NameMixin.set_rpc_actions)
  * [EventProperty](#components.gpio.gpioz.core.input_devices.EventProperty)
  * [ButtonBase](#components.gpio.gpioz.core.input_devices.ButtonBase)
    * [value](#components.gpio.gpioz.core.input_devices.ButtonBase.value)
    * [pin](#components.gpio.gpioz.core.input_devices.ButtonBase.pin)
    * [pull\_up](#components.gpio.gpioz.core.input_devices.ButtonBase.pull_up)
    * [close](#components.gpio.gpioz.core.input_devices.ButtonBase.close)
  * [Button](#components.gpio.gpioz.core.input_devices.Button)
    * [on\_press](#components.gpio.gpioz.core.input_devices.Button.on_press)
  * [LongPressButton](#components.gpio.gpioz.core.input_devices.LongPressButton)
    * [on\_press](#components.gpio.gpioz.core.input_devices.LongPressButton.on_press)
  * [ShortLongPressButton](#components.gpio.gpioz.core.input_devices.ShortLongPressButton)
  * [RotaryEncoder](#components.gpio.gpioz.core.input_devices.RotaryEncoder)
    * [pin\_a](#components.gpio.gpioz.core.input_devices.RotaryEncoder.pin_a)
    * [pin\_b](#components.gpio.gpioz.core.input_devices.RotaryEncoder.pin_b)
    * [on\_rotate\_clockwise](#components.gpio.gpioz.core.input_devices.RotaryEncoder.on_rotate_clockwise)
    * [on\_rotate\_counter\_clockwise](#components.gpio.gpioz.core.input_devices.RotaryEncoder.on_rotate_counter_clockwise)
    * [close](#components.gpio.gpioz.core.input_devices.RotaryEncoder.close)
  * [TwinButton](#components.gpio.gpioz.core.input_devices.TwinButton)
    * [StateVar](#components.gpio.gpioz.core.input_devices.TwinButton.StateVar)
    * [close](#components.gpio.gpioz.core.input_devices.TwinButton.close)
    * [value](#components.gpio.gpioz.core.input_devices.TwinButton.value)
    * [is\_active](#components.gpio.gpioz.core.input_devices.TwinButton.is_active)
* [components.gpio.gpioz.plugin.connectivity](#components.gpio.gpioz.plugin.connectivity)
  * [BUZZ\_TONE](#components.gpio.gpioz.plugin.connectivity.BUZZ_TONE)
  * [register\_rfid\_callback](#components.gpio.gpioz.plugin.connectivity.register_rfid_callback)
  * [register\_status\_led\_callback](#components.gpio.gpioz.plugin.connectivity.register_status_led_callback)
  * [register\_status\_buzzer\_callback](#components.gpio.gpioz.plugin.connectivity.register_status_buzzer_callback)
  * [register\_status\_tonalbuzzer\_callback](#components.gpio.gpioz.plugin.connectivity.register_status_tonalbuzzer_callback)
  * [register\_audio\_sink\_change\_callback](#components.gpio.gpioz.plugin.connectivity.register_audio_sink_change_callback)
  * [register\_volume\_led\_callback](#components.gpio.gpioz.plugin.connectivity.register_volume_led_callback)
  * [register\_volume\_buzzer\_callback](#components.gpio.gpioz.plugin.connectivity.register_volume_buzzer_callback)
  * [register\_volume\_rgbled\_callback](#components.gpio.gpioz.plugin.connectivity.register_volume_rgbled_callback)
* [components.gpio.gpioz.plugin](#components.gpio.gpioz.plugin)
  * [output\_devices](#components.gpio.gpioz.plugin.output_devices)
  * [input\_devices](#components.gpio.gpioz.plugin.input_devices)
  * [factory](#components.gpio.gpioz.plugin.factory)
  * [IS\_ENABLED](#components.gpio.gpioz.plugin.IS_ENABLED)
  * [IS\_MOCKED](#components.gpio.gpioz.plugin.IS_MOCKED)
  * [CONFIG\_FILE](#components.gpio.gpioz.plugin.CONFIG_FILE)
  * [ServiceIsRunningCallbacks](#components.gpio.gpioz.plugin.ServiceIsRunningCallbacks)
    * [register](#components.gpio.gpioz.plugin.ServiceIsRunningCallbacks.register)
    * [run\_callbacks](#components.gpio.gpioz.plugin.ServiceIsRunningCallbacks.run_callbacks)
  * [service\_is\_running\_callbacks](#components.gpio.gpioz.plugin.service_is_running_callbacks)
  * [build\_output\_device](#components.gpio.gpioz.plugin.build_output_device)
  * [build\_input\_device](#components.gpio.gpioz.plugin.build_input_device)
  * [get\_output](#components.gpio.gpioz.plugin.get_output)
  * [on](#components.gpio.gpioz.plugin.on)
  * [off](#components.gpio.gpioz.plugin.off)
  * [set\_value](#components.gpio.gpioz.plugin.set_value)
  * [flash](#components.gpio.gpioz.plugin.flash)
* [components.rfid.configure](#components.rfid.configure)
  * [reader\_install\_dependencies](#components.rfid.configure.reader_install_dependencies)
  * [reader\_load\_module](#components.rfid.configure.reader_load_module)
  * [query\_user\_for\_reader](#components.rfid.configure.query_user_for_reader)
  * [write\_config](#components.rfid.configure.write_config)
* [components.rfid](#components.rfid)
* [components.rfid.cardutils](#components.rfid.cardutils)
  * [decode\_card\_command](#components.rfid.cardutils.decode_card_command)
  * [card\_command\_to\_str](#components.rfid.cardutils.card_command_to_str)
  * [card\_to\_str](#components.rfid.cardutils.card_to_str)
* [components.rfid.cards](#components.rfid.cards)
  * [list\_cards](#components.rfid.cards.list_cards)
  * [delete\_card](#components.rfid.cards.delete_card)
  * [register\_card](#components.rfid.cards.register_card)
  * [register\_card\_custom](#components.rfid.cards.register_card_custom)
  * [save\_card\_database](#components.rfid.cards.save_card_database)
* [components.rfid.readerbase](#components.rfid.readerbase)
  * [ReaderBaseClass](#components.rfid.readerbase.ReaderBaseClass)
* [components.rfid.reader](#components.rfid.reader)
  * [RfidCardDetectCallbacks](#components.rfid.reader.RfidCardDetectCallbacks)
    * [register](#components.rfid.reader.RfidCardDetectCallbacks.register)
    * [run\_callbacks](#components.rfid.reader.RfidCardDetectCallbacks.run_callbacks)
  * [rfid\_card\_detect\_callbacks](#components.rfid.reader.rfid_card_detect_callbacks)
  * [CardRemovalTimerClass](#components.rfid.reader.CardRemovalTimerClass)
    * [\_\_init\_\_](#components.rfid.reader.CardRemovalTimerClass.__init__)
* [components.rfid.hardware.rdm6300\_serial.description](#components.rfid.hardware.rdm6300_serial.description)
* [components.rfid.hardware.rdm6300\_serial.rdm6300\_serial](#components.rfid.hardware.rdm6300_serial.rdm6300_serial)
  * [decode](#components.rfid.hardware.rdm6300_serial.rdm6300_serial.decode)
* [components.rfid.hardware.template\_new\_reader.description](#components.rfid.hardware.template_new_reader.description)
* [components.rfid.hardware.template\_new\_reader.template\_new\_reader](#components.rfid.hardware.template_new_reader.template_new_reader)
  * [query\_customization](#components.rfid.hardware.template_new_reader.template_new_reader.query_customization)
  * [ReaderClass](#components.rfid.hardware.template_new_reader.template_new_reader.ReaderClass)
    * [\_\_init\_\_](#components.rfid.hardware.template_new_reader.template_new_reader.ReaderClass.__init__)
    * [cleanup](#components.rfid.hardware.template_new_reader.template_new_reader.ReaderClass.cleanup)
    * [stop](#components.rfid.hardware.template_new_reader.template_new_reader.ReaderClass.stop)
    * [read\_card](#components.rfid.hardware.template_new_reader.template_new_reader.ReaderClass.read_card)
* [components.rfid.hardware.generic\_nfcpy.description](#components.rfid.hardware.generic_nfcpy.description)
* [components.rfid.hardware.generic\_nfcpy.generic\_nfcpy](#components.rfid.hardware.generic_nfcpy.generic_nfcpy)
  * [ReaderClass](#components.rfid.hardware.generic_nfcpy.generic_nfcpy.ReaderClass)
    * [cleanup](#components.rfid.hardware.generic_nfcpy.generic_nfcpy.ReaderClass.cleanup)
    * [stop](#components.rfid.hardware.generic_nfcpy.generic_nfcpy.ReaderClass.stop)
    * [read\_card](#components.rfid.hardware.generic_nfcpy.generic_nfcpy.ReaderClass.read_card)
* [components.rfid.hardware.generic\_usb.description](#components.rfid.hardware.generic_usb.description)
* [components.rfid.hardware.generic\_usb.generic\_usb](#components.rfid.hardware.generic_usb.generic_usb)
* [components.rfid.hardware.fake\_reader\_gui.fake\_reader\_gui](#components.rfid.hardware.fake_reader_gui.fake_reader_gui)
* [components.rfid.hardware.fake\_reader\_gui.description](#components.rfid.hardware.fake_reader_gui.description)
* [components.rfid.hardware.fake\_reader\_gui.gpioz\_gui\_addon](#components.rfid.hardware.fake_reader_gui.gpioz_gui_addon)
  * [create\_inputs](#components.rfid.hardware.fake_reader_gui.gpioz_gui_addon.create_inputs)
  * [set\_state](#components.rfid.hardware.fake_reader_gui.gpioz_gui_addon.set_state)
  * [que\_set\_state](#components.rfid.hardware.fake_reader_gui.gpioz_gui_addon.que_set_state)
  * [fix\_state](#components.rfid.hardware.fake_reader_gui.gpioz_gui_addon.fix_state)
  * [pbox\_set\_state](#components.rfid.hardware.fake_reader_gui.gpioz_gui_addon.pbox_set_state)
  * [que\_set\_pbox](#components.rfid.hardware.fake_reader_gui.gpioz_gui_addon.que_set_pbox)
  * [create\_outputs](#components.rfid.hardware.fake_reader_gui.gpioz_gui_addon.create_outputs)
* [components.rfid.hardware.pn532\_i2c\_py532.pn532\_i2c\_py532](#components.rfid.hardware.pn532_i2c_py532.pn532_i2c_py532)
* [components.rfid.hardware.pn532\_i2c\_py532.description](#components.rfid.hardware.pn532_i2c_py532.description)
* [components.rfid.hardware.rc522\_spi.rc522\_spi](#components.rfid.hardware.rc522_spi.rc522_spi)
* [components.rfid.hardware.rc522\_spi.description](#components.rfid.hardware.rc522_spi.description)
* [components.player](#components.player)
  * [MusicLibPath](#components.player.MusicLibPath)
  * [get\_music\_library\_path](#components.player.get_music_library_path)
* [components.battery\_monitor.batt\_mon\_i2c\_ina219](#components.battery_monitor.batt_mon_i2c_ina219)
  * [battmon\_ina219](#components.battery_monitor.batt_mon_i2c_ina219.battmon_ina219)
* [components.battery\_monitor.batt\_mon\_i2c\_ads1015](#components.battery_monitor.batt_mon_i2c_ads1015)
  * [battmon\_ads1015](#components.battery_monitor.batt_mon_i2c_ads1015.battmon_ads1015)
* [components.battery\_monitor.batt\_mon\_simulator](#components.battery_monitor.batt_mon_simulator)
  * [battmon\_simulator](#components.battery_monitor.batt_mon_simulator.battmon_simulator)
* [components.battery\_monitor.BatteryMonitorBase](#components.battery_monitor.BatteryMonitorBase)
  * [pt1\_frac](#components.battery_monitor.BatteryMonitorBase.pt1_frac)
  * [BattmonBase](#components.battery_monitor.BatteryMonitorBase.BattmonBase)
* [components.battery\_monitor](#components.battery_monitor)
* [components.controls.bluetooth\_audio\_buttons](#components.controls.bluetooth_audio_buttons)
* [components.controls.event\_devices](#components.controls.event_devices)
  * [IS\_ENABLED](#components.controls.event_devices.IS_ENABLED)
  * [CONFIG\_FILE](#components.controls.event_devices.CONFIG_FILE)
  * [activate](#components.controls.event_devices.activate)
  * [initialize](#components.controls.event_devices.initialize)
  * [parse\_device\_config](#components.controls.event_devices.parse_device_config)
* [components.controls.common.evdev\_listener](#components.controls.common.evdev_listener)
  * [find\_device](#components.controls.common.evdev_listener.find_device)
  * [EvDevKeyListener](#components.controls.common.evdev_listener.EvDevKeyListener)
    * [\_\_init\_\_](#components.controls.common.evdev_listener.EvDevKeyListener.__init__)
    * [run](#components.controls.common.evdev_listener.EvDevKeyListener.run)
    * [start](#components.controls.common.evdev_listener.EvDevKeyListener.start)
* [components.controls](#components.controls)
* [components.misc](#components.misc)
  * [rpc\_cmd\_help](#components.misc.rpc_cmd_help)
  * [get\_all\_loaded\_packages](#components.misc.get_all_loaded_packages)
  * [get\_all\_failed\_packages](#components.misc.get_all_failed_packages)
  * [get\_start\_time](#components.misc.get_start_time)
  * [get\_log](#components.misc.get_log)
  * [get\_log\_debug](#components.misc.get_log_debug)
  * [get\_log\_error](#components.misc.get_log_error)
  * [get\_git\_state](#components.misc.get_git_state)
  * [empty\_rpc\_call](#components.misc.empty_rpc_call)
  * [get\_app\_settings](#components.misc.get_app_settings)
  * [set\_app\_settings](#components.misc.set_app_settings)
* [components.publishing](#components.publishing)
  * [republish](#components.publishing.republish)
* [jukebox](#jukebox)
* [jukebox.callingback](#jukebox.callingback)
  * [CallbackHandler](#jukebox.callingback.CallbackHandler)
    * [register](#jukebox.callingback.CallbackHandler.register)
    * [run\_callbacks](#jukebox.callingback.CallbackHandler.run_callbacks)
    * [has\_callbacks](#jukebox.callingback.CallbackHandler.has_callbacks)
* [jukebox.plugs](#jukebox.plugs)
  * [PluginPackageClass](#jukebox.plugs.PluginPackageClass)
  * [register](#jukebox.plugs.register)
  * [register](#jukebox.plugs.register)
  * [register](#jukebox.plugs.register)
  * [register](#jukebox.plugs.register)
  * [register](#jukebox.plugs.register)
  * [register](#jukebox.plugs.register)
  * [tag](#jukebox.plugs.tag)
  * [initialize](#jukebox.plugs.initialize)
  * [finalize](#jukebox.plugs.finalize)
  * [atexit](#jukebox.plugs.atexit)
  * [load](#jukebox.plugs.load)
  * [load\_all\_named](#jukebox.plugs.load_all_named)
  * [load\_all\_unnamed](#jukebox.plugs.load_all_unnamed)
  * [load\_all\_finalize](#jukebox.plugs.load_all_finalize)
  * [close\_down](#jukebox.plugs.close_down)
  * [call](#jukebox.plugs.call)
  * [call\_ignore\_errors](#jukebox.plugs.call_ignore_errors)
  * [exists](#jukebox.plugs.exists)
  * [get](#jukebox.plugs.get)
  * [loaded\_as](#jukebox.plugs.loaded_as)
  * [delete](#jukebox.plugs.delete)
  * [dump\_plugins](#jukebox.plugs.dump_plugins)
  * [summarize](#jukebox.plugs.summarize)
  * [generate\_help\_rst](#jukebox.plugs.generate_help_rst)
  * [get\_all\_loaded\_packages](#jukebox.plugs.get_all_loaded_packages)
  * [get\_all\_failed\_packages](#jukebox.plugs.get_all_failed_packages)
* [jukebox.cfghandler](#jukebox.cfghandler)
  * [ConfigHandler](#jukebox.cfghandler.ConfigHandler)
    * [loaded\_from](#jukebox.cfghandler.ConfigHandler.loaded_from)
    * [get](#jukebox.cfghandler.ConfigHandler.get)
    * [setdefault](#jukebox.cfghandler.ConfigHandler.setdefault)
    * [getn](#jukebox.cfghandler.ConfigHandler.getn)
    * [setn](#jukebox.cfghandler.ConfigHandler.setn)
    * [setndefault](#jukebox.cfghandler.ConfigHandler.setndefault)
    * [config\_dict](#jukebox.cfghandler.ConfigHandler.config_dict)
    * [is\_modified](#jukebox.cfghandler.ConfigHandler.is_modified)
    * [clear\_modified](#jukebox.cfghandler.ConfigHandler.clear_modified)
    * [save](#jukebox.cfghandler.ConfigHandler.save)
    * [load](#jukebox.cfghandler.ConfigHandler.load)
  * [get\_handler](#jukebox.cfghandler.get_handler)
  * [load\_yaml](#jukebox.cfghandler.load_yaml)
  * [write\_yaml](#jukebox.cfghandler.write_yaml)
* [jukebox.speaking\_text](#jukebox.speaking_text)
* [jukebox.utils](#jukebox.utils)
  * [decode\_rpc\_call](#jukebox.utils.decode_rpc_call)
  * [decode\_rpc\_command](#jukebox.utils.decode_rpc_command)
  * [decode\_and\_call\_rpc\_command](#jukebox.utils.decode_and_call_rpc_command)
  * [bind\_rpc\_command](#jukebox.utils.bind_rpc_command)
  * [rpc\_call\_to\_str](#jukebox.utils.rpc_call_to_str)
  * [get\_config\_action](#jukebox.utils.get_config_action)
  * [generate\_cmd\_alias\_rst](#jukebox.utils.generate_cmd_alias_rst)
  * [generate\_cmd\_alias\_reference](#jukebox.utils.generate_cmd_alias_reference)
  * [get\_git\_state](#jukebox.utils.get_git_state)
* [jukebox.version](#jukebox.version)
  * [version](#jukebox.version.version)
  * [version\_info](#jukebox.version.version_info)
* [jukebox.playlistgenerator](#jukebox.playlistgenerator)
  * [TYPE\_DECODE](#jukebox.playlistgenerator.TYPE_DECODE)
  * [PlaylistCollector](#jukebox.playlistgenerator.PlaylistCollector)
    * [\_\_init\_\_](#jukebox.playlistgenerator.PlaylistCollector.__init__)
    * [set\_exclusion\_endings](#jukebox.playlistgenerator.PlaylistCollector.set_exclusion_endings)
    * [get\_directory\_content](#jukebox.playlistgenerator.PlaylistCollector.get_directory_content)
    * [parse](#jukebox.playlistgenerator.PlaylistCollector.parse)
* [jukebox.multitimer](#jukebox.multitimer)
  * [MultiTimer](#jukebox.multitimer.MultiTimer)
    * [cancel](#jukebox.multitimer.MultiTimer.cancel)
  * [GenericTimerClass](#jukebox.multitimer.GenericTimerClass)
    * [\_\_init\_\_](#jukebox.multitimer.GenericTimerClass.__init__)
    * [start](#jukebox.multitimer.GenericTimerClass.start)
    * [cancel](#jukebox.multitimer.GenericTimerClass.cancel)
    * [toggle](#jukebox.multitimer.GenericTimerClass.toggle)
    * [trigger](#jukebox.multitimer.GenericTimerClass.trigger)
    * [is\_alive](#jukebox.multitimer.GenericTimerClass.is_alive)
    * [get\_timeout](#jukebox.multitimer.GenericTimerClass.get_timeout)
    * [set\_timeout](#jukebox.multitimer.GenericTimerClass.set_timeout)
    * [publish](#jukebox.multitimer.GenericTimerClass.publish)
    * [get\_state](#jukebox.multitimer.GenericTimerClass.get_state)
  * [GenericEndlessTimerClass](#jukebox.multitimer.GenericEndlessTimerClass)
  * [GenericMultiTimerClass](#jukebox.multitimer.GenericMultiTimerClass)
    * [\_\_init\_\_](#jukebox.multitimer.GenericMultiTimerClass.__init__)
    * [start](#jukebox.multitimer.GenericMultiTimerClass.start)
* [jukebox.NvManager](#jukebox.NvManager)
* [jukebox.publishing.subscriber](#jukebox.publishing.subscriber)
* [jukebox.publishing](#jukebox.publishing)
  * [get\_publisher](#jukebox.publishing.get_publisher)
* [jukebox.publishing.server](#jukebox.publishing.server)
  * [PublishServer](#jukebox.publishing.server.PublishServer)
    * [run](#jukebox.publishing.server.PublishServer.run)
    * [handle\_message](#jukebox.publishing.server.PublishServer.handle_message)
    * [handle\_subscription](#jukebox.publishing.server.PublishServer.handle_subscription)
  * [Publisher](#jukebox.publishing.server.Publisher)
    * [\_\_init\_\_](#jukebox.publishing.server.Publisher.__init__)
    * [send](#jukebox.publishing.server.Publisher.send)
    * [revoke](#jukebox.publishing.server.Publisher.revoke)
    * [resend](#jukebox.publishing.server.Publisher.resend)
    * [close\_server](#jukebox.publishing.server.Publisher.close_server)
* [jukebox.daemon](#jukebox.daemon)
  * [log\_active\_threads](#jukebox.daemon.log_active_threads)
  * [JukeBox](#jukebox.daemon.JukeBox)
    * [signal\_handler](#jukebox.daemon.JukeBox.signal_handler)
* [jukebox.rpc.client](#jukebox.rpc.client)
* [jukebox.rpc](#jukebox.rpc)
* [jukebox.rpc.server](#jukebox.rpc.server)
  * [RpcServer](#jukebox.rpc.server.RpcServer)
    * [\_\_init\_\_](#jukebox.rpc.server.RpcServer.__init__)
    * [run](#jukebox.rpc.server.RpcServer.run)
* [misc](#misc)
  * [recursive\_chmod](#misc.recursive_chmod)
  * [flatten](#misc.flatten)
  * [getattr\_hierarchical](#misc.getattr_hierarchical)
* [misc.simplecolors](#misc.simplecolors)
  * [Colors](#misc.simplecolors.Colors)
  * [resolve](#misc.simplecolors.resolve)
  * [print](#misc.simplecolors.print)
* [misc.inputminus](#misc.inputminus)
  * [input\_int](#misc.inputminus.input_int)
  * [input\_yesno](#misc.inputminus.input_yesno)
* [misc.loggingext](#misc.loggingext)
  * [ColorFilter](#misc.loggingext.ColorFilter)
    * [\_\_init\_\_](#misc.loggingext.ColorFilter.__init__)
  * [PubStream](#misc.loggingext.PubStream)
  * [PubStreamHandler](#misc.loggingext.PubStreamHandler)

<a id="run_jukebox"></a>

# run\_jukebox

This is the main app and starts the Jukebox Core.

Usually this runs as a service, which is started automatically after boot-up. At times, it may be necessary to restart
the service.
For example after a configuration change. Not all configuration changes can be applied on-the-fly.
See [Jukebox Configuration](../../builders/configuration.md#jukebox-configuration).

For debugging, it is usually desirable to run the Jukebox directly from the console rather than
as service. This gives direct logging info in the console and allows changing command line parameters.
See [Troubleshooting](../../builders/troubleshooting.md).


<a id="run_rpc_tool"></a>

# run\_rpc\_tool

Command Line Interface to the Jukebox RPC Server

A command line tool for sending RPC commands to the running jukebox app.
This uses the same interface as the WebUI. Can be used for additional control
or for debugging.

The tool features auto-completion and command history.

The list of available commands is fetched from the running Jukebox service.

.. todo:
   - kwargs support


<a id="run_rpc_tool.get_common_beginning"></a>

#### get\_common\_beginning

```python
def get_common_beginning(strings)
```

Return the strings that are common to the beginning of each string in the strings list.


<a id="run_rpc_tool.runcmd"></a>

#### runcmd

```python
def runcmd(cmd)
```

Just run a command.

Right now duplicates more or less main()
:todo remove duplication of code


<a id="run_register_rfid_reader"></a>

# run\_register\_rfid\_reader

Setup tool to configure the RFID Readers.

Run this once to register and configure the RFID readers with the Jukebox. Can be re-run at any time to change
the settings. For more information see [RFID Readers](../rfid/README.md).

> [!NOTE]
> This tool will always write a new configurations file. Thus, overwrite the old one (after checking with the user).
> Any manual modifications to the settings will have to be re-applied


<a id="run_publicity_sniffer"></a>

# run\_publicity\_sniffer

A command line tool that monitors all messages being sent out from the

Jukebox via the publishing interface.  Received messages are printed in the console.
Mainly used for debugging.


<a id="__init__"></a>

# \_\_init\_\_

<a id="run_configure_audio"></a>

# run\_configure\_audio

Setup tool to register the PulseAudio sinks as primary and secondary audio outputs.

Will also setup equalizer and mono down mixer in the pulseaudio config file.

Run this once after installation. Can be re-run at any time to change the settings.
For more information see [Audio Configuration](../../builders/audio.md#audio-configuration).


<a id="components"></a>

# components

<a id="components.mqtt.utils"></a>

# components.mqtt.utils

<a id="components.mqtt.utils.play_folder_recursive_args"></a>

#### play\_folder\_recursive\_args

```python
def play_folder_recursive_args(payload: str) -> dict
```

Create arguments for playing a folder recursively.


<a id="components.mqtt.utils.parse_repeat_mode"></a>

#### parse\_repeat\_mode

```python
def parse_repeat_mode(payload: str) -> Optional[str]
```

Parse a repeat mode command based on the given payload.


<a id="components.mqtt.utils.get_args"></a>

#### get\_args

```python
def get_args(config: dict, payload: dict) -> Optional[dict]
```

Retrieve arguments based on the configuration and payload.


<a id="components.mqtt.utils.get_rpc_command"></a>

#### get\_rpc\_command

```python
def get_rpc_command(config: dict) -> Optional[dict]
```

Retrieve the RPC command based on the configuration.


<a id="components.mqtt.utils.get_kwargs"></a>

#### get\_kwargs

```python
def get_kwargs(config: dict, payload: dict) -> Optional[dict]
```

Retrieve keyword arguments based on the configuration and payload.


<a id="components.mqtt.utils.get_current_time_milli"></a>

#### get\_current\_time\_milli

```python
def get_current_time_milli() -> int
```

Get the current time in milliseconds.


<a id="components.mqtt.utils.split_topic"></a>

#### split\_topic

```python
def split_topic(topic: str) -> str
```

Split an MQTT topic and return a part of it.


<a id="components.mqtt.utils.map_repeat_mode"></a>

#### map\_repeat\_mode

```python
def map_repeat_mode(repeat_active: bool, single_active: bool) -> str
```

Map boolean flags to repeat mode constants.


<a id="components.mqtt.mqtt_command_alias"></a>

# components.mqtt.mqtt\_command\_alias

This file provides definitions for MQTT to RPC command aliases

See []
See [RPC Commands](../../builders/rpc-commands.md)


<a id="components.mqtt.mqtt_command_alias.get_mute"></a>

#### get\_mute

```python
def get_mute(payload) -> bool
```

Helper to toggle mute in legacy support.


<a id="components.mqtt.mqtt_const"></a>

# components.mqtt.mqtt\_const

<a id="components.mqtt"></a>

# components.mqtt

<a id="components.mqtt.MQTT"></a>

## MQTT Objects

```python
class MQTT(threading.Thread)
```

A thread for monitoring events and publishing interesting events via MQTT.


<a id="components.mqtt.MQTT.run"></a>

#### run

```python
def run() -> None
```

Main loop of the MQTT thread.


<a id="components.mqtt.MQTT.stop"></a>

#### stop

```python
def stop()
```

Stop the MQTT thread.


<a id="components.mqtt.on_connect"></a>

#### on\_connect

```python
def on_connect(client, userdata, flags, rc)
```

Start thread on successful MQTT connection.


<a id="components.mqtt.initialize"></a>

#### initialize

```python
@plugs.initialize
def initialize()
```

Setup connection and trigger the MQTT loop.


<a id="components.volume"></a>

# components.volume

PulseAudio Volume Control Plugin Package

## Features

* Volume Control
* Two outputs
* Watcher thread on volume / output change

## Publishes

* volume.level
* volume.sink

## PulseAudio References

<https://brokkr.net/2018/05/24/down-the-drain-the-elusive-default-pulseaudio-sink/>

Check fallback device (on device de-connect):

    $ pacmd list-sinks | grep -e 'name:' -e 'index'


## Integration

Pulse Audio runs as a user process. Processes who want to communicate / stream to it
must also run as a user process.

This means must also run as user process, as described in
[Music Player Daemon](../../builders/system.md#music-player-daemon-mpd).

## Misc

PulseAudio may switch the sink automatically to a connecting bluetooth device depending on the loaded module
with name module-switch-on-connect. On Raspberry Pi OS Bullseye, this module is not part of the default configuration
in ``/usr/pulse/default.pa``. So, we don't need to worry about it.
If the module gets loaded it conflicts with the toggle on connect and the selected primary / secondary outputs
from the Jukebox. Remove it from the configuration!

    ### Use hot-plugged devices like Bluetooth or USB automatically (LP: `1702794`)
    ### not available on PI?
    .ifexists module-switch-on-connect.so
    load-module module-switch-on-connect
    .endif

## Why PulseAudio?

The audio configuration of the system is one of those topics,
which has a myriad of options and possibilities. Every system is different and PulseAudio unifies these and
makes our life easier. Besides, it is only option to support Bluetooth at the moment.

## Callbacks:

The following callbacks are provided. Register callbacks with these adder functions (see their documentation for details):

1. :func:`add_on_connect_callback`
2. :func:`add_on_output_change_callbacks`
3. :func:`add_on_volume_change_callback`


<a id="components.volume.PulseMonitor"></a>

## PulseMonitor Objects

```python
class PulseMonitor(threading.Thread)
```

A thread for monitoring and interacting with the Pulse Lib via pulsectrl

Whenever we want to access pulsectl, we need to exit the event listen loop.
This is handled by the context manager. It stops the event loop and returns
the pulsectl instance to be used (it does no return the monitor thread itself!)

The context manager also locks the module to ensure proper thread sequencing,
as only a single thread may work with pulsectl at any time. Currently, an RLock is
used, even if it may not be necessary


<a id="components.volume.PulseMonitor.SoundCardConnectCallbacks"></a>

## SoundCardConnectCallbacks Objects

```python
class SoundCardConnectCallbacks(CallbackHandler)
```

Callbacks are executed when

* new sound card gets connected


<a id="components.volume.PulseMonitor.SoundCardConnectCallbacks.register"></a>

#### register

```python
def register(func: Callable[[str, str], None])
```

Add a new callback function :attr:`func`.

Callback signature is

.. py:function:: func(card_driver: str, device_name: str)
    :noindex:

**Arguments**:

- `card_driver`: The PulseAudio card driver module,
e.g. :data:`module-bluez5-device.c` or :data:`module-alsa-card.c`
- `device_name`: The sound card device name as reported
in device properties

<a id="components.volume.PulseMonitor.SoundCardConnectCallbacks.run_callbacks"></a>

#### run\_callbacks

```python
def run_callbacks(sink_name, alias, sink_index, error_state)
```



<a id="components.volume.PulseMonitor.toggle_on_connect"></a>

#### toggle\_on\_connect

```python
@property
def toggle_on_connect()
```

Returns :data:`True` if the sound card shall be changed when a new card connects/disconnects. Setting this

property changes the behavior.

> [!NOTE]
> A new card is always assumed to be the secondary device from the audio configuration.
> At the moment there is no check it actually is the configured device. This means any new
> device connection will initiate the toggle. This, however, is no real issue as the RPi's audio
> system will be relatively stable once setup


<a id="components.volume.PulseMonitor.toggle_on_connect"></a>

#### toggle\_on\_connect

```python
@toggle_on_connect.setter
def toggle_on_connect(state=True)
```

Toggle Doc 2


<a id="components.volume.PulseMonitor.stop"></a>

#### stop

```python
def stop()
```

Stop the pulse monitor thread


<a id="components.volume.PulseMonitor.run"></a>

#### run

```python
def run() -> None
```

Starts the pulse monitor thread


<a id="components.volume.PulseVolumeControl"></a>

## PulseVolumeControl Objects

```python
class PulseVolumeControl()
```

Volume control manager for PulseAudio

When accessing the pulse library, it needs to be put into a special
state. Which is ensured by the context manager

    with pulse_monitor as pulse ...


All private functions starting with `_function_name` assume that this is ensured by
the calling function. All user functions acquire proper context!


<a id="components.volume.PulseVolumeControl.OutputChangeCallbackHandler"></a>

## OutputChangeCallbackHandler Objects

```python
class OutputChangeCallbackHandler(CallbackHandler)
```

Callbacks are executed when

* audio sink is changed


<a id="components.volume.PulseVolumeControl.OutputChangeCallbackHandler.register"></a>

#### register

```python
def register(func: Callable[[str, str, int, int], None])
```

Add a new callback function :attr:`func`.

Parameters always give the valid audio sink. That means, if an error
occurred, all parameters are valid.

Callback signature is

.. py:function:: func(sink_name: str, alias: str, sink_index: int, error_state: int)
    :noindex:

**Arguments**:

- `sink_name`: PulseAudio's sink name
- `alias`: The alias for :attr:`sink_name`
- `sink_index`: The index of the sink in the configuration list
- `error_state`: 1 if there was an attempt to change the output
but an error occurred. Above parameters always give the now valid sink!
If a sink change is successful, it is 0.

<a id="components.volume.PulseVolumeControl.OutputChangeCallbackHandler.run_callbacks"></a>

#### run\_callbacks

```python
def run_callbacks(sink_name, alias, sink_index, error_state)
```



<a id="components.volume.PulseVolumeControl.OutputVolumeCallbackHandler"></a>

## OutputVolumeCallbackHandler Objects

```python
class OutputVolumeCallbackHandler(CallbackHandler)
```

Callbacks are executed when

* audio volume level is changed


<a id="components.volume.PulseVolumeControl.OutputVolumeCallbackHandler.register"></a>

#### register

```python
def register(func: Callable[[int, bool, bool], None])
```

Add a new callback function :attr:`func`.

Callback signature is

.. py:function:: func(volume: int, is_min: bool, is_max: bool)
    :noindex:

**Arguments**:

- `volume`: Volume level
- `is_min`: 1, if volume level is minimum, else 0
- `is_max`: 1, if volume level is maximum, else 0

<a id="components.volume.PulseVolumeControl.OutputVolumeCallbackHandler.run_callbacks"></a>

#### run\_callbacks

```python
def run_callbacks(sink_name, alias, sink_index, error_state)
```



<a id="components.volume.PulseVolumeControl.toggle_output"></a>

#### toggle\_output

```python
@plugin.tag
def toggle_output()
```

Toggle the audio output sink


<a id="components.volume.PulseVolumeControl.get_outputs"></a>

#### get\_outputs

```python
@plugin.tag
def get_outputs()
```

Get current output and list of outputs


<a id="components.volume.PulseVolumeControl.publish_volume"></a>

#### publish\_volume

```python
@plugin.tag
def publish_volume()
```

Publish (volume, mute)


<a id="components.volume.PulseVolumeControl.publish_outputs"></a>

#### publish\_outputs

```python
@plugin.tag
def publish_outputs()
```

Publish current output and list of outputs


<a id="components.volume.PulseVolumeControl.set_volume"></a>

#### set\_volume

```python
@plugin.tag
def set_volume(volume: int)
```

Set the volume (0-100) for the currently active output


<a id="components.volume.PulseVolumeControl.get_volume"></a>

#### get\_volume

```python
@plugin.tag
def get_volume()
```

Get the volume


<a id="components.volume.PulseVolumeControl.change_volume"></a>

#### change\_volume

```python
@plugin.tag
def change_volume(step: int)
```

Increase/decrease the volume by step for the currently active output


<a id="components.volume.PulseVolumeControl.get_mute"></a>

#### get\_mute

```python
@plugin.tag
def get_mute()
```

Return mute status for the currently active output


<a id="components.volume.PulseVolumeControl.mute"></a>

#### mute

```python
@plugin.tag
def mute(mute=True)
```

Set mute status for the currently active output


<a id="components.volume.PulseVolumeControl.set_output"></a>

#### set\_output

```python
@plugin.tag
def set_output(sink_index: int)
```

Set the active output (sink_index = 0: primary, 1: secondary)


<a id="components.volume.PulseVolumeControl.set_soft_max_volume"></a>

#### set\_soft\_max\_volume

```python
@plugin.tag
def set_soft_max_volume(max_volume: int)
```

Limit the maximum volume to max_volume for the currently active output


<a id="components.volume.PulseVolumeControl.get_soft_max_volume"></a>

#### get\_soft\_max\_volume

```python
@plugin.tag
def get_soft_max_volume()
```

Return the maximum volume limit for the currently active output


<a id="components.volume.PulseVolumeControl.card_list"></a>

#### card\_list

```python
def card_list() -> List[pulsectl.PulseCardInfo]
```

Return the list of present sound card


<a id="components.rpc_command_alias"></a>

# components.rpc\_command\_alias

This file provides definitions for RPC command aliases

See [RPC Commands](../../builders/rpc-commands.md)


<a id="components.synchronisation"></a>

# components.synchronisation

<a id="components.synchronisation.syncutils"></a>

# components.synchronisation.syncutils

<a id="components.synchronisation.rfidcards"></a>

# components.synchronisation.rfidcards

Handles the synchronisation of RFID cards (audiofolder and card database entries).

sync-all -> all card entries and audiofolders are synced from remote including deletions
sync-on-scan -> only the entry and audiofolder for the cardId will be synced from remote.
                Deletions are only performed on files and subfolder inside the audiofolder.
                A deletion of the audiofolder itself on remote side will not be propagated.

card database:
On synchronisation the remote file will not be synced with the original cards database, but rather a local copy.
If a full sync is performed, the state is written back to the original file.
If a single card sync is performed, only the state of the specific cardId is updated in the original file.
This is done to allow to play audio offline.
Otherwise we would also update other cardIds where the audiofolders have not been synced yet.
The local copy is kept to reduce unnecessary syncing.


<a id="components.synchronisation.rfidcards.SyncRfidcards"></a>

## SyncRfidcards Objects

```python
class SyncRfidcards()
```

Control class for sync RFID cards functionality


<a id="components.synchronisation.rfidcards.SyncRfidcards.sync_change_on_rfid_scan"></a>

#### sync\_change\_on\_rfid\_scan

```python
@plugs.tag
def sync_change_on_rfid_scan(option: str = 'toggle') -> None
```

Change activation of 'on_rfid_scan_enabled'

**Arguments**:

- `option`: Must be one of 'enable', 'disable', 'toggle'

<a id="components.synchronisation.rfidcards.SyncRfidcards.sync_all"></a>

#### sync\_all

```python
@plugs.tag
def sync_all() -> bool
```

Sync all audiofolder and cardids from the remote server.

Removes local entries not existing at the remote server.


<a id="components.synchronisation.rfidcards.SyncRfidcards.sync_card_database"></a>

#### sync\_card\_database

```python
@plugs.tag
def sync_card_database(card_id: str) -> bool
```

Sync the card database from the remote server, if existing.

If card_id is provided only this entry is updated.

**Arguments**:

- `card_id`: The cardid to update

<a id="components.synchronisation.rfidcards.SyncRfidcards.sync_folder"></a>

#### sync\_folder

```python
@plugs.tag
def sync_folder(folder: str) -> bool
```

Sync the folder from the remote server, if existing

**Arguments**:

- `folder`: Folder path relative to music library path

<a id="components.jingle.jinglemp3"></a>

# components.jingle.jinglemp3

Generic MP3 jingle Service for jingle.JingleFactory


<a id="components.jingle.jinglemp3.JingleMp3Play"></a>

## JingleMp3Play Objects

```python
@plugin.register(auto_tag=True)
class JingleMp3Play()
```

Jingle Service for playing MP3 files


<a id="components.jingle.jinglemp3.JingleMp3Play.play"></a>

#### play

```python
def play(filename)
```

Play the MP3 file


<a id="components.jingle.jinglemp3.JingleMp3PlayBuilder"></a>

## JingleMp3PlayBuilder Objects

```python
class JingleMp3PlayBuilder()
```

<a id="components.jingle.jinglemp3.JingleMp3PlayBuilder.__init__"></a>

#### \_\_init\_\_

```python
def __init__()
```

Builder instantiates JingleMp3Play during init and not during first call because

we want JingleMp3Play registers as plugin function in any case if this plugin is loaded
(and not only on first use!)


<a id="components.jingle"></a>

# components.jingle

Jingle Playback Factory for extensible run-time support of various file types


<a id="components.jingle.JingleFactory"></a>

## JingleFactory Objects

```python
class JingleFactory()
```

Jingle Factory


<a id="components.jingle.JingleFactory.list"></a>

#### list

```python
def list()
```

List the available volume services


<a id="components.jingle.play"></a>

#### play

```python
@plugin.register
def play(filename)
```

Play the jingle using the configured jingle service

> [!NOTE]
> This runs in a separate thread. And this may cause troubles
> when changing the volume level before
> and after the sound playback: There is nothing to prevent another
> thread from changing the volume and sink while playback happens
> and afterwards we change the volume back to where it was before!

There is no way around this dilemma except for not running the jingle as a
separate thread. Currently (as thread) even the RPC is started before the sound
is finished and the volume is reset to normal...

However: Volume plugin is loaded before jingle and sets the default
volume. No interference here. It can now only happen
if (a) through the RPC or (b) some other plugin the volume is changed. Okay, now
(a) let's hope that there is enough delay in the user requesting a volume change
(b) let's hope no other plugin wants to do that
(c) no bluetooth device connects during this time (and pulseaudio control is set to toggle_on_connect)
and take our changes with the threaded approach.


<a id="components.jingle.play_startup"></a>

#### play\_startup

```python
@plugin.register
def play_startup()
```

Play the startup sound (using jingle.play)


<a id="components.jingle.play_shutdown"></a>

#### play\_shutdown

```python
@plugin.register
def play_shutdown()
```

Play the shutdown sound (using jingle.play)


<a id="components.jingle.alsawave"></a>

# components.jingle.alsawave

ALSA wave jingle Service for jingle.JingleFactory


<a id="components.jingle.alsawave.AlsaWave"></a>

## AlsaWave Objects

```python
@plugin.register
class AlsaWave()
```

Jingle Service for playing wave files directly from Python through ALSA


<a id="components.jingle.alsawave.AlsaWave.play"></a>

#### play

```python
@plugin.tag
def play(filename)
```

Play the wave file


<a id="components.jingle.alsawave.AlsaWaveBuilder"></a>

## AlsaWaveBuilder Objects

```python
class AlsaWaveBuilder()
```

<a id="components.jingle.alsawave.AlsaWaveBuilder.__init__"></a>

#### \_\_init\_\_

```python
def __init__()
```

Builder instantiates AlsaWave during init and not during first call because

we want AlsaWave registers as plugin function in any case if this plugin is loaded
(and not only on first use!)


<a id="components.hostif.linux"></a>

# components.hostif.linux

<a id="components.hostif.linux.shutdown"></a>

#### shutdown

```python
@plugin.register
def shutdown()
```

Shutdown the host machine


<a id="components.hostif.linux.reboot"></a>

#### reboot

```python
@plugin.register
def reboot()
```

Reboot the host machine


<a id="components.hostif.linux.jukebox_is_service"></a>

#### jukebox\_is\_service

```python
@plugin.register
def jukebox_is_service()
```

Check if current Jukebox process is running as a service


<a id="components.hostif.linux.is_any_jukebox_service_active"></a>

#### is\_any\_jukebox\_service\_active

```python
@plugin.register
def is_any_jukebox_service_active()
```

Check if a Jukebox service is running

> [!NOTE]
> Does not have the be the current app, that is running as a service!


<a id="components.hostif.linux.restart_service"></a>

#### restart\_service

```python
@plugin.register
def restart_service()
```

Restart Jukebox App if running as a service


<a id="components.hostif.linux.get_disk_usage"></a>

#### get\_disk\_usage

```python
@plugin.register()
def get_disk_usage(path='/')
```

Return the disk usage in Megabytes as dictionary for RPC export


<a id="components.hostif.linux.get_cpu_temperature"></a>

#### get\_cpu\_temperature

```python
@plugin.register
def get_cpu_temperature()
```

Get the CPU temperature with single decimal point

No error handling: this is expected to take place up-level!


<a id="components.hostif.linux.get_ip_address"></a>

#### get\_ip\_address

```python
@plugin.register
def get_ip_address()
```

Get the IP address


<a id="components.hostif.linux.wlan_disable_power_down"></a>

#### wlan\_disable\_power\_down

```python
@plugin.register()
def wlan_disable_power_down(card=None)
```

Turn off power management of wlan. Keep RPi reachable via WLAN

This must be done after every reboot
card=None takes card from configuration file


<a id="components.hostif.linux.get_autohotspot_status"></a>

#### get\_autohotspot\_status

```python
@plugin.register
def get_autohotspot_status()
```

Get the status of the auto hotspot feature


<a id="components.hostif.linux.stop_autohotspot"></a>

#### stop\_autohotspot

```python
@plugin.register()
def stop_autohotspot()
```

Stop auto hotspot functionality

Stopping and disabling the timer and running the service one last time manually


<a id="components.hostif.linux.start_autohotspot"></a>

#### start\_autohotspot

```python
@plugin.register()
def start_autohotspot()
```

Start auto hotspot functionality

Enabling and starting the timer (timer will start the service)


<a id="components.timers"></a>

# components.timers

<a id="components.playermpd.coverart_cache_manager"></a>

# components.playermpd.coverart\_cache\_manager

<a id="components.playermpd.playcontentcallback"></a>

# components.playermpd.playcontentcallback

<a id="components.playermpd.playcontentcallback.PlayContentCallbacks"></a>

## PlayContentCallbacks Objects

```python
class PlayContentCallbacks(Generic[STATE], CallbackHandler)
```

Callbacks are executed in various play functions


<a id="components.playermpd.playcontentcallback.PlayContentCallbacks.register"></a>

#### register

```python
def register(func: Callable[[str, STATE], None])
```

Add a new callback function :attr:`func`.

Callback signature is

.. py:function:: func(folder: str, state: STATE)
    :noindex:

**Arguments**:

- `folder`: relativ path to folder to play
- `state`: indicator of the state inside the calling

<a id="components.playermpd.playcontentcallback.PlayContentCallbacks.run_callbacks"></a>

#### run\_callbacks

```python
def run_callbacks(folder: str, state: STATE)
```



<a id="components.playermpd"></a>

# components.playermpd

Package for interfacing with the MPD Music Player Daemon

Status information in three topics
1) Player Status: published only on change
  This is a subset of the MPD status (and not the full MPD status) ??
  - folder
  - song
  - volume (volume is published only via player status, and not separatly to avoid too many Threads)
  - ...
2) Elapsed time: published every 250 ms, unless constant
  - elapsed
3) Folder Config: published only on change
   This belongs to the folder being played
   Publish:
   - random, resume, single, loop
   On save store this information:
   Contains the information for resume functionality of each folder
   - random, resume, single, loop
   - if resume:
     - current song, elapsed
   - what is PLAYSTATUS for?
   When to save
   - on stop
   Angstsave:
   - on pause (only if box get turned off without proper shutdown - else stop gets implicitly called)
   - on status change of random, resume, single, loop (for resume omit current status if currently playing- this has now meaning)
   Load checks:
   - if resume, but no song, elapsed -> log error and start from the beginning

Status storing:
  - Folder config for each folder (see above)
  - Information to restart last folder playback, which is:
    - last_folder -> folder_on_close
    - song, elapsed
    - random, resume, single, loop
    - if resume is enabled, after start we need to set last_played_folder, such that card swipe is detected as second swipe?!
      on the other hand: if resume is enabled, this is also saved to folder.config -> and that is checked by play card

Internal status
  - last played folder: Needed to detect second swipe


Saving {'player_status': {'last_played_folder': 'TraumfaengerStarkeLieder', 'CURRENTSONGPOS': '0', 'CURRENTFILENAME': 'TraumfaengerStarkeLieder/01.mp3'},
'audio_folder_status':
{'TraumfaengerStarkeLieder': {'ELAPSED': '1.0', 'CURRENTFILENAME': 'TraumfaengerStarkeLieder/01.mp3', 'CURRENTSONGPOS': '0', 'PLAYSTATUS': 'stop', 'RESUME': 'OFF', 'SHUFFLE': 'OFF', 'LOOP': 'OFF', 'SINGLE': 'OFF'},
'Giraffenaffen': {'ELAPSED': '1.0', 'CURRENTFILENAME': 'TraumfaengerStarkeLieder/01.mp3', 'CURRENTSONGPOS': '0', 'PLAYSTATUS': 'play', 'RESUME': 'OFF', 'SHUFFLE': 'OFF', 'LOOP': 'OFF', 'SINGLE': 'OFF'}}}

References:
https://github.com/Mic92/python-mpd2
https://python-mpd2.readthedocs.io/en/latest/topics/commands.html
https://mpd.readthedocs.io/en/latest/protocol.html

sudo -u mpd speaker-test -t wav -c 2


<a id="components.playermpd.PlayerMPD"></a>

## PlayerMPD Objects

```python
class PlayerMPD()
```

Interface to MPD Music Player Daemon


<a id="components.playermpd.PlayerMPD.mpd_retry_with_mutex"></a>

#### mpd\_retry\_with\_mutex

```python
def mpd_retry_with_mutex(mpd_cmd, *args)
```

This method adds thread saftey for acceses to mpd via a mutex lock,

it shall be used for each access to mpd to ensure thread safety
In case of a communication error the connection will be reestablished and the pending command will be repeated 2 times

I think this should be refactored to a decorator


<a id="components.playermpd.PlayerMPD.pause"></a>

#### pause

```python
@plugs.tag
def pause(state: int = 1)
```

Enforce pause to state (1: pause, 0: resume)

This is what you want as card removal action: pause the playback, so it can be resumed when card is placed
on the reader again. What happens on re-placement depends on configured second swipe option


<a id="components.playermpd.PlayerMPD.next"></a>

#### next

```python
@plugs.tag
def next()
```

Play next track in current playlist


<a id="components.playermpd.PlayerMPD.rewind"></a>

#### rewind

```python
@plugs.tag
def rewind()
```

Re-start current playlist from first track

Note: Will not re-read folder config, but leave settings untouched


<a id="components.playermpd.PlayerMPD.replay"></a>

#### replay

```python
@plugs.tag
def replay()
```

Re-start playing the last-played folder

Will reset settings to folder config


<a id="components.playermpd.PlayerMPD.toggle"></a>

#### toggle

```python
@plugs.tag
def toggle()
```

Toggle pause state, i.e. do a pause / resume depending on current state


<a id="components.playermpd.PlayerMPD.replay_if_stopped"></a>

#### replay\_if\_stopped

```python
@plugs.tag
def replay_if_stopped()
```

Re-start playing the last-played folder unless playlist is still playing

> [!NOTE]
> To me this seems much like the behaviour of play,
> but we keep it as it is specifically implemented in box 2.X


<a id="components.playermpd.PlayerMPD.play_card"></a>

#### play\_card

```python
@plugs.tag
def play_card(folder: str, recursive: bool = False)
```

Main entry point for trigger music playing from RFID reader. Decodes second swipe options before playing folder content

Checks for second (or multiple) trigger of the same folder and calls first swipe / second swipe action
accordingly.

**Arguments**:

- `folder`: Folder path relative to music library path
- `recursive`: Add folder recursively

<a id="components.playermpd.PlayerMPD.flush_coverart_cache"></a>

#### flush\_coverart\_cache

```python
@plugs.tag
def flush_coverart_cache()
```

Deletes the Cover Art Cache


<a id="components.playermpd.PlayerMPD.get_folder_content"></a>

#### get\_folder\_content

```python
@plugs.tag
def get_folder_content(folder: str)
```

Get the folder content as content list with meta-information. Depth is always 1.

Call repeatedly to descend in hierarchy

**Arguments**:

- `folder`: Folder path relative to music library path

<a id="components.playermpd.PlayerMPD.play_folder"></a>

#### play\_folder

```python
@plugs.tag
def play_folder(folder: str, recursive: bool = False) -> None
```

Playback a music folder.

Folder content is added to the playlist as described by :mod:`jukebox.playlistgenerator`.
The playlist is cleared first.

**Arguments**:

- `folder`: Folder path relative to music library path
- `recursive`: Add folder recursively

<a id="components.playermpd.PlayerMPD.play_album"></a>

#### play\_album

```python
@plugs.tag
def play_album(albumartist: str, album: str)
```

Playback a album found in MPD database.

All album songs are added to the playlist
The playlist is cleared first.

**Arguments**:

- `albumartist`: Artist of the Album provided by MPD database
- `album`: Album name provided by MPD database

<a id="components.playermpd.PlayerMPD.get_volume"></a>

#### get\_volume

```python
def get_volume()
```

Get the current volume

For volume control do not use directly, but use through the plugin 'volume',
as the user may have configured a volume control manager other than MPD


<a id="components.playermpd.PlayerMPD.set_volume"></a>

#### set\_volume

```python
def set_volume(volume)
```

Set the volume

For volume control do not use directly, but use through the plugin 'volume',
as the user may have configured a volume control manager other than MPD


<a id="components.playermpd.play_card_callbacks"></a>

#### play\_card\_callbacks

Callback handler instance for play_card events.

- is executed when play_card function is called
States:
- See :class:`PlayCardState`
See :class:`PlayContentCallbacks`


<a id="components.gpio.gpioz.core.converter"></a>

# components.gpio.gpioz.core.converter

Provides converter functions/classes for various Jukebox parameters to

values that can be assigned to GPIO output devices


<a id="components.gpio.gpioz.core.converter.ColorProperty"></a>

## ColorProperty Objects

```python
class ColorProperty()
```

Color descriptor ensuring valid weight ranges


<a id="components.gpio.gpioz.core.converter.VolumeToRGB"></a>

## VolumeToRGB Objects

```python
class VolumeToRGB()
```

Converts linear volume level to an RGB color value running through the color spectrum

**Arguments**:

- `max_input`: Maximum input value of linear input data
- `offset`: Offset in degrees in the color circle. Color circle
traverses blue (0), cyan(60), green (120), yellow(180), red (240), magenta (340)
- `section`: The section of the full color circle to use in degrees
Map input :data:`0...100` to color range :data:`green...magenta` and get the color for level 50

    conv = VolumeToRGB(100, offset=120, section=180)
    (r, g, b) = conv(50)

The three components of an RGB LEDs do not have the same luminosity.
Weight factors are used to get a balanced color output

<a id="components.gpio.gpioz.core.converter.VolumeToRGB.__call__"></a>

#### \_\_call\_\_

```python
def __call__(volume) -> Tuple[float, float, float]
```

Perform conversion for single volume level

**Returns**:

Tuple(red, green, blue)

<a id="components.gpio.gpioz.core.converter.VolumeToRGB.luminize"></a>

#### luminize

```python
def luminize(r, g, b)
```

Apply the color weight factors to the input color values


<a id="components.gpio.gpioz.core.mock"></a>

# components.gpio.gpioz.core.mock

Changes to the GPIOZero devices for using with the Mock RFID Reader


<a id="components.gpio.gpioz.core.mock.patch_mock_outputs_with_callback"></a>

#### patch\_mock\_outputs\_with\_callback

```python
def patch_mock_outputs_with_callback()
```

Monkey Patch LED + Buzzer to get a callback when state changes

This targets to represent the state in the TK GUI.
Other output devices cannot be represented in the GUI and are silently ignored.

> [!NOTE]
> Only for developing purposes!


<a id="components.gpio.gpioz.core.output_devices"></a>

# components.gpio.gpioz.core.output\_devices

Provides all supported output devices for the GPIOZ plugin.

For each device all constructor parameters can be set via the configuration file. Only exceptions
are the :attr:`name` and :attr:`pin_factory` which are set by internal mechanisms.

The devices a are a relatively thin wrapper around the GPIOZero devices with the same name.
We add a name property to be used for error log message and similar and a :func:`flash` function
to all devices. This function provides a unified API to all devices. This means it can be called for every device
with parameters for this device and optional parameters from another device. Unused/unsupported parameters
are silently ignored. This is done to reduce the amount of coding required for connectivity functions.

For examples how to use the devices from the configuration files, see
[GPIO: Output Devices](../../builders/gpio.md#output-devices).


<a id="components.gpio.gpioz.core.output_devices.LED"></a>

## LED Objects

```python
class LED(NameMixin, gpiozero.LED)
```

A binary LED

**Arguments**:

- `pin`: The GPIO pin which the LED is connected
- `active_high`: If :data:`true` the output pin will have a high logic level when the device is turned on.
- `pin_factory`: The GPIOZero pin factory. This parameter cannot be set through the configuration file
- `name` (`str`): The name of the button for use in error messages. This parameter cannot be set explicitly
through the configuration file

<a id="components.gpio.gpioz.core.output_devices.LED.flash"></a>

#### flash

```python
def flash(on_time=1, off_time=1, n=1, *, background=True, **ignored_kwargs)
```

Exactly like :func:`blink` but restores the original state after flashing the device

**Arguments**:

- `on_time` (`float`): Number of seconds on. Defaults to 1 second.
- `off_time` (`float`): Number of seconds off. Defaults to 1 second.
- `n`: Number of times to blink; :data:`None` means forever.
- `background` (`bool`): If :data:`True` (the default), start a background thread to
continue blinking and return immediately. If :data:`False`, only
return when the blink is finished
- `ignored_kwargs`: Ignore all other keywords so this function can be called with identical
parameters also for all other output devices

<a id="components.gpio.gpioz.core.output_devices.Buzzer"></a>

## Buzzer Objects

```python
class Buzzer(NameMixin, gpiozero.Buzzer)
```

<a id="components.gpio.gpioz.core.output_devices.Buzzer.flash"></a>

#### flash

```python
def flash(on_time=1, off_time=1, n=1, *, background=True, **ignored_kwargs)
```

Flash the device and restore the previous value afterwards


<a id="components.gpio.gpioz.core.output_devices.PWMLED"></a>

## PWMLED Objects

```python
class PWMLED(NameMixin, gpiozero.PWMLED)
```

<a id="components.gpio.gpioz.core.output_devices.PWMLED.flash"></a>

#### flash

```python
def flash(on_time=1,
          off_time=1,
          n=1,
          *,
          fade_in_time=0,
          fade_out_time=0,
          background=True,
          **ignored_kwargs)
```

Flash the LED and restore the previous value afterwards


<a id="components.gpio.gpioz.core.output_devices.RGBLED"></a>

## RGBLED Objects

```python
class RGBLED(NameMixin, gpiozero.RGBLED)
```

<a id="components.gpio.gpioz.core.output_devices.RGBLED.flash"></a>

#### flash

```python
def flash(on_time=1,
          off_time=1,
          *,
          fade_in_time=0,
          fade_out_time=0,
          on_color=(1, 1, 1),
          off_color=(0, 0, 0),
          n=None,
          background=True,
          **igorned_kwargs)
```

Flash the LED with :attr:`on_color` and restore the previous value afterwards


<a id="components.gpio.gpioz.core.output_devices.TonalBuzzer"></a>

## TonalBuzzer Objects

```python
class TonalBuzzer(NameMixin, gpiozero.TonalBuzzer)
```

<a id="components.gpio.gpioz.core.output_devices.TonalBuzzer.flash"></a>

#### flash

```python
def flash(on_time=1,
          off_time=1,
          n=1,
          *,
          tone=None,
          background=True,
          **ignored_kwargs)
```

Play the tone :data:`tone` for :attr:`n` times


<a id="components.gpio.gpioz.core.output_devices.TonalBuzzer.melody"></a>

#### melody

```python
def melody(on_time=0.2,
           off_time=0.05,
           *,
           tone: Optional[List[Tone]] = None,
           background=True)
```

Play a melody from the list of tones in :attr:`tone`


<a id="components.gpio.gpioz.core.input_devices"></a>

# components.gpio.gpioz.core.input\_devices

Provides all supported input devices for the GPIOZ plugin.

Input devices are based on GPIOZero devices. So for certain configuration parameters, you should
their documentation.

All callback handlers are replaced by GPIOZ callback handlers. These are usually configured
by using the :func:`set_rpc_actions` each input device exhibits.

For examples how to use the devices from the configuration files, see
[GPIO: Input Devices](../../builders/gpio.md#input-devices).


<a id="components.gpio.gpioz.core.input_devices.NameMixin"></a>

## NameMixin Objects

```python
class NameMixin(ABC)
```

Provides name property and RPC decode function


<a id="components.gpio.gpioz.core.input_devices.NameMixin.set_rpc_actions"></a>

#### set\_rpc\_actions

```python
@abstractmethod
def set_rpc_actions(action_config) -> None
```

Set all input device callbacks from :attr:`action_config`

**Arguments**:

- `action_config`: Dictionary with one
[RPC Commands](../../builders/rpc-commands.md) definition entry for every device callback

<a id="components.gpio.gpioz.core.input_devices.EventProperty"></a>

## EventProperty Objects

```python
class EventProperty()
```

Event callback property


<a id="components.gpio.gpioz.core.input_devices.ButtonBase"></a>

## ButtonBase Objects

```python
class ButtonBase(ABC)
```

Common stuff for single button devices


<a id="components.gpio.gpioz.core.input_devices.ButtonBase.value"></a>

#### value

```python
@property
def value()
```

Returns 1 if the button is currently pressed, and 0 if it is not.


<a id="components.gpio.gpioz.core.input_devices.ButtonBase.pin"></a>

#### pin

```python
@property
def pin()
```

Returns the underlying pin class from GPIOZero.


<a id="components.gpio.gpioz.core.input_devices.ButtonBase.pull_up"></a>

#### pull\_up

```python
@property
def pull_up()
```

If :data:`True`, the device uses an internal pull-up resistor to set the GPIO pin “high” by default.


<a id="components.gpio.gpioz.core.input_devices.ButtonBase.close"></a>

#### close

```python
def close()
```

Close the device and release the pin


<a id="components.gpio.gpioz.core.input_devices.Button"></a>

## Button Objects

```python
class Button(NameMixin, ButtonBase)
```

A basic Button that runs a single actions on button press

**Arguments**:

- `pull_up` (`bool`): If :data:`True`, the device uses an internal pull-up resistor to set the GPIO pin “high” by default.
If :data:`False` the internal pull-down resistor is used. If :data:`None`, the pin will be floating and an external
resistor must be used and the :attr:`active_state` must be set.
- `active_state` (`bool or None`): If :data:`True`, when the hardware pin state is ``HIGH``, the software
pin is ``HIGH``. If :data:`False`, the input polarity is reversed: when
the hardware pin state is ``HIGH``, the software pin state is ``LOW``.
Use this parameter to set the active state of the underlying pin when
configuring it as not pulled (when *pull_up* is :data:`None`). When
*pull_up* is :data:`True` or :data:`False`, the active state is
automatically set to the proper value.
- `bounce_time` (`float or None`): Specifies the length of time (in seconds) that the component will
ignore changes in state after an initial change. This defaults to
:data:`None` which indicates that no bounce compensation will be
performed.
- `hold_repeat` (`bool`): If :data:`True` repeat the :attr:`on_press` every :attr:`hold_time` seconds. Else action
is run only once independent of the length of time the button is pressed for.
- `hold_time` (`float`): Time in seconds to wait between invocations of :attr:`on_press`.
- `pin_factory`: The GPIOZero pin factory. This parameter cannot be set through the configuration file
- `name` (`str`): The name of the button for use in error messages. This parameter cannot be set explicitly
through the configuration file

.. copied from GPIOZero's documentation: active_state, bounce_time
.. Copyright Ben Nuttall / SPDX-License-Identifier: BSD-3-Clause

<a id="components.gpio.gpioz.core.input_devices.Button.on_press"></a>

#### on\_press

```python
@property
def on_press()
```

The function to run when the device has been pressed


<a id="components.gpio.gpioz.core.input_devices.LongPressButton"></a>

## LongPressButton Objects

```python
class LongPressButton(NameMixin, ButtonBase)
```

A Button that runs a single actions only when the button is pressed long enough

**Arguments**:

- `pull_up`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)
- `active_state`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)
- `bounce_time`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)
- `hold_repeat`: If :data:`True` repeat the :attr:`on_press` every :attr:`hold_time` seconds. Else only action
is run only once independent of the length of time the button is pressed for.
- `hold_time`: The minimum time, the button must be pressed be running :attr:`on_press` for the first time.
Also the time in seconds to wait between invocations of :attr:`on_press`.

<a id="components.gpio.gpioz.core.input_devices.LongPressButton.on_press"></a>

#### on\_press

```python
@on_press.setter
def on_press(func)
```

The function to run when the device has been pressed for longer than :attr:`hold_time`


<a id="components.gpio.gpioz.core.input_devices.ShortLongPressButton"></a>

## ShortLongPressButton Objects

```python
class ShortLongPressButton(NameMixin, ButtonBase)
```

A single button that runs two different actions depending if the button is pressed for a short or long time.

The shortest possible time is used to ensure a unique identification to an action can be made. For example a short press
can only be identified, when a button is released before :attr:`hold_time`, i.e. not directly on button press.
But a long press can be identified as soon as :attr:`hold_time` is reached and there is no need to wait for the release
event. Furthermore, if there is a long hold, only the long hold action is executed - the short press action is not run
in this case!

**Arguments**:

- `pull_up`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)
- `active_state`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)
- `bounce_time`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)
- `hold_time`: The time in seconds to differentiate if it is a short or long press. If the button is released before
this time, it is a short press. As soon as the button is held for :attr:`hold_time` it is a long press and the
short press action is ignored
- `hold_repeat`: If :data:`True` repeat the long press action every :attr:`hold_time` seconds after first long press
action
- `pin_factory`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)
- `name`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)

<a id="components.gpio.gpioz.core.input_devices.RotaryEncoder"></a>

## RotaryEncoder Objects

```python
class RotaryEncoder(NameMixin)
```

A rotary encoder to run one of two actions depending on the rotation direction.

**Arguments**:

- `bounce_time`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)
- `pin_factory`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)
- `name`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)

<a id="components.gpio.gpioz.core.input_devices.RotaryEncoder.pin_a"></a>

#### pin\_a

```python
@property
def pin_a()
```

Returns the underlying pin A


<a id="components.gpio.gpioz.core.input_devices.RotaryEncoder.pin_b"></a>

#### pin\_b

```python
@property
def pin_b()
```

Returns the underlying pin B


<a id="components.gpio.gpioz.core.input_devices.RotaryEncoder.on_rotate_clockwise"></a>

#### on\_rotate\_clockwise

```python
@property
def on_rotate_clockwise()
```

The function to run when the encoder is rotated clockwise


<a id="components.gpio.gpioz.core.input_devices.RotaryEncoder.on_rotate_counter_clockwise"></a>

#### on\_rotate\_counter\_clockwise

```python
@property
def on_rotate_counter_clockwise()
```

The function to run when the encoder is rotated counter clockwise


<a id="components.gpio.gpioz.core.input_devices.RotaryEncoder.close"></a>

#### close

```python
def close()
```

Close the device and release the pin


<a id="components.gpio.gpioz.core.input_devices.TwinButton"></a>

## TwinButton Objects

```python
class TwinButton(NameMixin)
```

A two-button device which can run up to six different actions, a.k.a the six function beast.

Per user press "input" of the TwinButton, only a single callback is executed (but this callback
may be executed several times).
The shortest possible time is used to ensure a unique identification to an action can be made. For example a short press
can only be identified, when a button is released before :attr:`hold_time`, i.e. not directly on button press.
But a long press can be identified as soon as :attr:`hold_time` is reached and there is no need to wait for the release
event. Furthermore, if there is a long hold, only the long hold action is executed - the short press action is not run
in this case!

It is not necessary to configure all actions.

**Arguments**:

- `pull_up`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)
- `active_state`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)
- `bounce_time`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)
- `hold_time`: The time in seconds to differentiate if it is a short or long press. If the button is released before
this time, it is a short press. As soon as the button is held for :attr:`hold_time` it is a long press and the
short press action is ignored.
- `hold_repeat`: If :data:`True` repeat the long press action every :attr:`hold_time` seconds after first long press
action. A long dual press is never repeated independent of this setting
- `pin_factory`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)
- `name`: See [`Button`](#components.gpio.gpioz.core.input_devices.Button)

<a id="components.gpio.gpioz.core.input_devices.TwinButton.StateVar"></a>

## StateVar Objects

```python
class StateVar(Enum)
```

State encoding of the Mealy FSM


<a id="components.gpio.gpioz.core.input_devices.TwinButton.close"></a>

#### close

```python
def close()
```

Close the device and release the pins


<a id="components.gpio.gpioz.core.input_devices.TwinButton.value"></a>

#### value

```python
@property
def value()
```

2 bit integer indicating if and which button is currently pressed. Button A is the LSB.


<a id="components.gpio.gpioz.core.input_devices.TwinButton.is_active"></a>

#### is\_active

```python
@property
def is_active()
```



<a id="components.gpio.gpioz.plugin.connectivity"></a>

# components.gpio.gpioz.plugin.connectivity

Provide connector functions to hook up to some kind of Jukebox functionality and change the output device's state

accordingly.

Connector functions can often be used for various output devices. Some connector functions are specific to
an output device type.


<a id="components.gpio.gpioz.plugin.connectivity.BUZZ_TONE"></a>

#### BUZZ\_TONE

The tone to be used as buzz tone when the buzzer is an active buzzer


<a id="components.gpio.gpioz.plugin.connectivity.register_rfid_callback"></a>

#### register\_rfid\_callback

```python
def register_rfid_callback(device)
```

Flash the output device once on successful RFID card detection and thrice if card ID is unknown

Compatible devices:

* :class:`components.gpio.gpioz.core.output_devices.LED`
* :class:`components.gpio.gpioz.core.output_devices.PWMLED`
* :class:`components.gpio.gpioz.core.output_devices.RGBLED`
* :class:`components.gpio.gpioz.core.output_devices.Buzzer`
* :class:`components.gpio.gpioz.core.output_devices.TonalBuzzer`


<a id="components.gpio.gpioz.plugin.connectivity.register_status_led_callback"></a>

#### register\_status\_led\_callback

```python
def register_status_led_callback(device)
```

Turn LED on when Jukebox App has started

Compatible devices:

* :class:`components.gpio.gpioz.core.output_devices.LED`
* :class:`components.gpio.gpioz.core.output_devices.PWMLED`
* :class:`components.gpio.gpioz.core.output_devices.RGBLED`


<a id="components.gpio.gpioz.plugin.connectivity.register_status_buzzer_callback"></a>

#### register\_status\_buzzer\_callback

```python
def register_status_buzzer_callback(device)
```

Buzz once when Jukebox App has started, twice when closing down

Compatible devices:

* :class:`components.gpio.gpioz.core.output_devices.Buzzer`
* :class:`components.gpio.gpioz.core.output_devices.TonalBuzzer`


<a id="components.gpio.gpioz.plugin.connectivity.register_status_tonalbuzzer_callback"></a>

#### register\_status\_tonalbuzzer\_callback

```python
def register_status_tonalbuzzer_callback(device)
```

Buzz a multi-note melody when Jukebox App has started and when closing down

Compatible devices:

* :class:`components.gpio.gpioz.core.output_devices.TonalBuzzer`


<a id="components.gpio.gpioz.plugin.connectivity.register_audio_sink_change_callback"></a>

#### register\_audio\_sink\_change\_callback

```python
def register_audio_sink_change_callback(device)
```

Turn LED on if secondary audio output is selected. If audio output change

fails, blink thrice

Compatible devices:

* :class:`components.gpio.gpioz.core.output_devices.LED`
* :class:`components.gpio.gpioz.core.output_devices.PWMLED`
* :class:`components.gpio.gpioz.core.output_devices.RGBLED`


<a id="components.gpio.gpioz.plugin.connectivity.register_volume_led_callback"></a>

#### register\_volume\_led\_callback

```python
def register_volume_led_callback(device)
```

Have a PWMLED change it's brightness according to current volume. LED flashes when minimum or maximum volume

is reached. Minimum value is still a very dimly turned on LED (i.e. LED is never off).

Compatible devices:

* :class:`components.gpio.gpioz.core.output_devices.PWMLED`


<a id="components.gpio.gpioz.plugin.connectivity.register_volume_buzzer_callback"></a>

#### register\_volume\_buzzer\_callback

```python
def register_volume_buzzer_callback(device)
```

Sound a buzzer once when minimum or maximum value is reached

Compatible devices:

* :class:`components.gpio.gpioz.core.output_devices.Buzzer`
* :class:`components.gpio.gpioz.core.output_devices.TonalBuzzer`


<a id="components.gpio.gpioz.plugin.connectivity.register_volume_rgbled_callback"></a>

#### register\_volume\_rgbled\_callback

```python
def register_volume_rgbled_callback(device)
```

Have a :class:`RGBLED` change it's color according to current volume. LED flashes when minimum or maximum volume

is reached.

Compatible devices:

* :class:`components.gpio.gpioz.core.output_devices.RGBLED`


<a id="components.gpio.gpioz.plugin"></a>

# components.gpio.gpioz.plugin

The GPIOZ plugin interface build all input and output devices from the configuration file and connects

the actions and callbacks. It also provides a very restricted, but common API for the output devices to the RPC.
That API is mainly used for testing. All the relevant output state changes are usually made through callbacks directly
using the output device's API.


<a id="components.gpio.gpioz.plugin.output_devices"></a>

#### output\_devices

List of all created output devices


<a id="components.gpio.gpioz.plugin.input_devices"></a>

#### input\_devices

List of all created input devices


<a id="components.gpio.gpioz.plugin.factory"></a>

#### factory

The global pin factory used in this module

Using different pin factories for different devices is not supported


<a id="components.gpio.gpioz.plugin.IS_ENABLED"></a>

#### IS\_ENABLED

Indicates that the GPIOZ module is enabled and loaded w/o errors


<a id="components.gpio.gpioz.plugin.IS_MOCKED"></a>

#### IS\_MOCKED

Indicates that the pin factory is a mock factory


<a id="components.gpio.gpioz.plugin.CONFIG_FILE"></a>

#### CONFIG\_FILE

The path of the config file the GPIOZ configuration was loaded from


<a id="components.gpio.gpioz.plugin.ServiceIsRunningCallbacks"></a>

## ServiceIsRunningCallbacks Objects

```python
class ServiceIsRunningCallbacks(CallbackHandler)
```

Callbacks are executed when

* Jukebox app started
* Jukebox shuts down

This is intended to e.g. signal an LED to change state.
This is integrated into this module because:

* we need the GPIO to control a LED (it must be available when the status callback comes)
* the plugin callback functions provide all the functionality to control the status of the LED
* which means no need to adapt other modules


<a id="components.gpio.gpioz.plugin.ServiceIsRunningCallbacks.register"></a>

#### register

```python
def register(func: Callable[[int], None])
```

Add a new callback function :attr:`func`.

Callback signature is

.. py:function:: func(status: int)
    :noindex:

**Arguments**:

- `status`: 1 if app started, 0 if app shuts down

<a id="components.gpio.gpioz.plugin.ServiceIsRunningCallbacks.run_callbacks"></a>

#### run\_callbacks

```python
def run_callbacks(status: int)
```



<a id="components.gpio.gpioz.plugin.service_is_running_callbacks"></a>

#### service\_is\_running\_callbacks

Callback handler instance for service_is_running_callbacks events.

See :class:`ServiceIsRunningCallbacks`


<a id="components.gpio.gpioz.plugin.build_output_device"></a>

#### build\_output\_device

```python
def build_output_device(name: str, config: Dict)
```

Construct and register a new output device

In principal all supported GPIOZero output devices can be used.
For all devices a custom functions need to be written to control the state of the outputs


<a id="components.gpio.gpioz.plugin.build_input_device"></a>

#### build\_input\_device

```python
def build_input_device(name: str, config)
```

Construct and connect a new input device

Supported input devices are those from gpio.gpioz.core.input_devices


<a id="components.gpio.gpioz.plugin.get_output"></a>

#### get\_output

```python
def get_output(name: str)
```

Get the output device instance based on the configured name

**Arguments**:

- `name`: The alias name output device instance

<a id="components.gpio.gpioz.plugin.on"></a>

#### on

```python
@plugin.register
def on(name: str)
```

Turn an output device on

**Arguments**:

- `name`: The alias name output device instance

<a id="components.gpio.gpioz.plugin.off"></a>

#### off

```python
@plugin.register
def off(name: str)
```

Turn an output device off

**Arguments**:

- `name`: The alias name output device instance

<a id="components.gpio.gpioz.plugin.set_value"></a>

#### set\_value

```python
@plugin.register
def set_value(name: str, value: Any)
```

Set the output device to :attr:`value`

**Arguments**:

- `name`: The alias name output device instance
- `value`: Value to set the device to

<a id="components.gpio.gpioz.plugin.flash"></a>

#### flash

```python
@plugin.register
def flash(name,
          on_time=1,
          off_time=1,
          n=1,
          *,
          fade_in_time=0,
          fade_out_time=0,
          tone=None,
          color=(1, 1, 1))
```

Flash (blink or beep) an output device

This is a generic function for all types of output devices. Parameters not applicable to an
specific output device are silently ignored

**Arguments**:

- `name`: The alias name output device instance
- `on_time`: Time in seconds in state ``ON``
- `off_time`: Time in seconds in state ``OFF``
- `n`: Number of flash cycles
- `tone`: The tone in to play, e.g. 'A4'. *Only for TonalBuzzer*.
- `color`: The RGB color *only for PWMLED*.
- `fade_in_time`: Time in seconds for transitioning to on. *Only for PWMLED and RGBLED*
- `fade_out_time`: Time in seconds for transitioning to off. *Only for PWMLED and RGBLED*

<a id="components.rfid.configure"></a>

# components.rfid.configure

<a id="components.rfid.configure.reader_install_dependencies"></a>

#### reader\_install\_dependencies

```python
def reader_install_dependencies(reader_path: str,
                                dependency_install: str) -> None
```

Install dependencies for the selected reader module

**Arguments**:

- `reader_path`: Path to the reader module
- `dependency_install`: how to handle installing of dependencies
'query': query user (default)
'auto': automatically
'no': don't install dependencies

<a id="components.rfid.configure.reader_load_module"></a>

#### reader\_load\_module

```python
def reader_load_module(reader_name)
```

Load the module for the reader_name

A ModuleNotFoundError is unrecoverable, but we at least want to give some hint how to resolve that to the user
All other errors will NOT be handled. Modules that do not load due to compile errors have other problems

**Arguments**:

- `reader_name`: Name of the reader to load the module for

**Returns**:

module

<a id="components.rfid.configure.query_user_for_reader"></a>

#### query\_user\_for\_reader

```python
def query_user_for_reader(dependency_install='query') -> dict
```

Ask the user to select a RFID reader and prompt for the reader's configuration

This function performs the following steps, to find and present all available readers to the user

- search for available reader subpackages
- dynamically load the description module for each reader subpackage
- queries user for selection
- if no_dep_install=False, install dependencies as given by requirements.txt and execute setup.inc.sh of subpackage
- dynamically load the actual reader module from the reader subpackage
- if selected reader has customization options query user for that now
- return configuration

There are checks to make sure we have the right reader modules and they are what we expect.
The are as few requirements towards the reader module as possible and everything else is optional
(see reader_template for these requirements)
However, there is no error handling w.r.t to user input and reader's query_config. Firstly, in this script
we cannot gracefully handle an exception that occurs on reader level, and secondly the exception will simply
exit the script w/o writing the config to file. No harm done.

This script expects to reside in the directory with all the reader subpackages, i.e it is part of the rfid-reader package.
Otherwise you'll need to adjust sys.path

**Arguments**:

- `dependency_install`: how to handle installing of dependencies
'query': query user (default)
'auto': automatically
'no': don't install dependencies

**Returns**:

`dict as {section: {parameter: value}}`: nested dict with entire configuration that can be read into ConfigParser

<a id="components.rfid.configure.write_config"></a>

#### write\_config

```python
def write_config(config_file: str,
                 config_dict: dict,
                 force_overwrite=False) -> None
```

Write configuration to config_file

**Arguments**:

- `config_file`: relative or absolute path to config file
- `config_dict`: nested dict with configuration parameters for ConfigParser consumption
- `force_overwrite`: overwrite existing configuration file without asking

<a id="components.rfid"></a>

# components.rfid

<a id="components.rfid.cardutils"></a>

# components.rfid.cardutils

Common card decoding functions

TODO: Thread safety when accessing the card DB!


<a id="components.rfid.cardutils.decode_card_command"></a>

#### decode\_card\_command

```python
def decode_card_command(cfg_rpc_cmd: Mapping, logger: logging.Logger = log)
```

Extension of utils.decode_action with card-specific parameters


<a id="components.rfid.cardutils.card_command_to_str"></a>

#### card\_command\_to\_str

```python
def card_command_to_str(cfg_rpc_cmd: Mapping, long=False) -> List[str]
```

Returns a list of strings with [card_action, ignore_same_id_delay, ignore_card_removal_action]

The last two parameters are only present, if *long* is True and if they are present in the cfg_rpc_cmd


<a id="components.rfid.cardutils.card_to_str"></a>

#### card\_to\_str

```python
def card_to_str(card_id: str, long=False) -> List[str]
```

Returns a list of strings from card entry command in the format of :func:`card_command_to_str`


<a id="components.rfid.cards"></a>

# components.rfid.cards

Handling the RFID card database

A few considerations:
- Changing the Card DB influences to current state
  - rfid.reader: Does not care, as it always freshly looks into the DB when a new card is triggered
  - fake_reader_gui: Initializes the Drop-down menu once on start --> Will get out of date!

Do we need a notifier? Or a callback for modules to get notified?
Do we want to publish the information about a card DB update?
TODO: Add callback for on_database_change

TODO: check card id type (if int, convert to str)
TODO: check if args is really a list (convert if not?)


<a id="components.rfid.cards.list_cards"></a>

#### list\_cards

```python
@plugs.register
def list_cards()
```

Provide a summarized, decoded list of all card actions

This is intended as basis for a formatter function

Format: 'id': {decoded_function_call, ignore_same_id_delay, ignore_card_removal_action, description, from_alias}


<a id="components.rfid.cards.delete_card"></a>

#### delete\_card

```python
@plugs.register
def delete_card(card_id: str, auto_save: bool = True)
```

**Arguments**:

- `auto_save`: 
- `card_id`: 

<a id="components.rfid.cards.register_card"></a>

#### register\_card

```python
@plugs.register
def register_card(card_id: str,
                  cmd_alias: str,
                  args: Optional[List] = None,
                  kwargs: Optional[Dict] = None,
                  ignore_card_removal_action: Optional[bool] = None,
                  ignore_same_id_delay: Optional[bool] = None,
                  overwrite: bool = False,
                  auto_save: bool = True)
```

Register a new card based on quick-selection

If you are going to call this through the RPC it will get a little verbose

**Example:** Registering a new card with ID *0009* for increment volume with a custom argument to inc_volume
(*here: 15*) and custom *ignore_same_id_delay value*::

    plugin.call_ignore_errors('cards', 'register_card',
                              args=['0009', 'inc_volume'],
                              kwargs={'args': [15], 'ignore_same_id_delay': True, 'overwrite': True})


<a id="components.rfid.cards.register_card_custom"></a>

#### register\_card\_custom

```python
@plugs.register
def register_card_custom()
```

Register a new card with full RPC call specification (Not implemented yet)


<a id="components.rfid.cards.save_card_database"></a>

#### save\_card\_database

```python
@plugs.register
def save_card_database(filename=None, *, only_if_changed=True)
```

Store the current card database. If filename is None, it is saved back to the file it was loaded from


<a id="components.rfid.readerbase"></a>

# components.rfid.readerbase

<a id="components.rfid.readerbase.ReaderBaseClass"></a>

## ReaderBaseClass Objects

```python
class ReaderBaseClass(ABC)
```

Abstract Base Class for all Reader Classes to ensure common API

Look at template_new_reader.py for documentation how to integrate a new RFID reader


<a id="components.rfid.reader"></a>

# components.rfid.reader

<a id="components.rfid.reader.RfidCardDetectCallbacks"></a>

## RfidCardDetectCallbacks Objects

```python
class RfidCardDetectCallbacks(CallbackHandler)
```

Callbacks are executed if rfid card is detected


<a id="components.rfid.reader.RfidCardDetectCallbacks.register"></a>

#### register

```python
def register(func: Callable[[str, RfidCardDetectState], None])
```

Add a new callback function :attr:`func`.

Callback signature is

.. py:function:: func(card_id: str, state: int)
    :noindex:

**Arguments**:

- `card_id`: Card ID
- `state`: See `RfidCardDetectState`

<a id="components.rfid.reader.RfidCardDetectCallbacks.run_callbacks"></a>

#### run\_callbacks

```python
def run_callbacks(card_id: str, state: RfidCardDetectState)
```



<a id="components.rfid.reader.rfid_card_detect_callbacks"></a>

#### rfid\_card\_detect\_callbacks

Callback handler instance for rfid_card_detect_callbacks events.

See [`RfidCardDetectCallbacks`](#components.rfid.reader.RfidCardDetectCallbacks)


<a id="components.rfid.reader.CardRemovalTimerClass"></a>

## CardRemovalTimerClass Objects

```python
class CardRemovalTimerClass(threading.Thread)
```

A timer watchdog thread that calls timeout_action on time-out


<a id="components.rfid.reader.CardRemovalTimerClass.__init__"></a>

#### \_\_init\_\_

```python
def __init__(on_timeout_callback, logger: logging.Logger = None)
```

**Arguments**:

- `on_timeout_callback`: The function to execute on time-out

<a id="components.rfid.hardware.rdm6300_serial.description"></a>

# components.rfid.hardware.rdm6300\_serial.description

<a id="components.rfid.hardware.rdm6300_serial.rdm6300_serial"></a>

# components.rfid.hardware.rdm6300\_serial.rdm6300\_serial

<a id="components.rfid.hardware.rdm6300_serial.rdm6300_serial.decode"></a>

#### decode

```python
def decode(raw_card_id: bytearray, number_format: int) -> str
```

Decode the RDM6300 data format into actual card ID


<a id="components.rfid.hardware.template_new_reader.description"></a>

# components.rfid.hardware.template\_new\_reader.description

Provide a short title for this reader.

This is what that user will see when asked for selecting his RFID reader
So, be precise but readable. Precise means 40 characters or less


<a id="components.rfid.hardware.template_new_reader.template_new_reader"></a>

# components.rfid.hardware.template\_new\_reader.template\_new\_reader

<a id="components.rfid.hardware.template_new_reader.template_new_reader.query_customization"></a>

#### query\_customization

```python
def query_customization() -> dict
```

Query the user for reader parameter customization

This function will be called during the configuration/setup phase when the user selects this reader module.
It must return all configuration parameters that are necessary to later use the Reader class.
You can ask the user for selections and choices. And/or provide default values.
If your reader requires absolutely no configuration return {}


<a id="components.rfid.hardware.template_new_reader.template_new_reader.ReaderClass"></a>

## ReaderClass Objects

```python
class ReaderClass(ReaderBaseClass)
```

The actual reader class that is used to read RFID cards.

It will be instantiated once and then read_card() is called in an endless loop.

It will be used in a  manner
  with Reader(reader_cfg_key) as reader:
    for card_id in reader:
      ...
which ensures proper resource de-allocation. For this to work derive this class from ReaderBaseClass.
All the required interfaces are implemented there.

Put your code into these functions (see below for more information)
  - `__init__`
  - read_card
  - cleanup
  - stop


<a id="components.rfid.hardware.template_new_reader.template_new_reader.ReaderClass.__init__"></a>

#### \_\_init\_\_

```python
def __init__(reader_cfg_key)
```

In the constructor, you will get the `reader_cfg_key` with which you can access the configuration data

As you are dealing directly with potentially user-manipulated config information, it is
advisable to do some sanity checks and give useful error messages. Even if you cannot recover gracefully,
a good error message helps :-)


<a id="components.rfid.hardware.template_new_reader.template_new_reader.ReaderClass.cleanup"></a>

#### cleanup

```python
def cleanup()
```

The cleanup function: free and release all resources used by this card reader (if any).

Put all your cleanup code here, e.g. if you are using the serial bus or GPIO pins.
Will be called implicitly via the __exit__ function
This function must exist! If there is nothing to do, just leave the pass statement in place below


<a id="components.rfid.hardware.template_new_reader.template_new_reader.ReaderClass.stop"></a>

#### stop

```python
def stop()
```

This function is called to tell the reader to exist it's reading function.

This function is called before cleanup is called.

> [!NOTE]
> This is usually called from a different thread than the reader's thread! And this is the reason for the
> two-step exit strategy. This function works across threads to indicate to the reader that is should stop attempt
> to read a card. Once called, the function read_card will not be called again. When the reader thread exits
> cleanup is called from the reader thread itself.


<a id="components.rfid.hardware.template_new_reader.template_new_reader.ReaderClass.read_card"></a>

#### read\_card

```python
def read_card() -> str
```

Blocking or non-blocking function that waits for a new card to appear and return the card's UID as string

This is were your main code goes :-)
This function must return a string with the card id
In case of error, it may return None or an empty string

The function should break and return with an empty string, once stop() is called


<a id="components.rfid.hardware.generic_nfcpy.description"></a>

# components.rfid.hardware.generic\_nfcpy.description

List of supported devices https://nfcpy.readthedocs.io/en/latest/overview.html


<a id="components.rfid.hardware.generic_nfcpy.generic_nfcpy"></a>

# components.rfid.hardware.generic\_nfcpy.generic\_nfcpy

<a id="components.rfid.hardware.generic_nfcpy.generic_nfcpy.ReaderClass"></a>

## ReaderClass Objects

```python
class ReaderClass(ReaderBaseClass)
```

The reader class for nfcpy supported NFC card readers.


<a id="components.rfid.hardware.generic_nfcpy.generic_nfcpy.ReaderClass.cleanup"></a>

#### cleanup

```python
def cleanup()
```

The cleanup function: free and release all resources used by this card reader (if any).


<a id="components.rfid.hardware.generic_nfcpy.generic_nfcpy.ReaderClass.stop"></a>

#### stop

```python
def stop()
```

This function is called to tell the reader to exit its reading function.


<a id="components.rfid.hardware.generic_nfcpy.generic_nfcpy.ReaderClass.read_card"></a>

#### read\_card

```python
def read_card() -> str
```

Blocking or non-blocking function that waits for a new card to appear and return the card's UID as string


<a id="components.rfid.hardware.generic_usb.description"></a>

# components.rfid.hardware.generic\_usb.description

<a id="components.rfid.hardware.generic_usb.generic_usb"></a>

# components.rfid.hardware.generic\_usb.generic\_usb

<a id="components.rfid.hardware.fake_reader_gui.fake_reader_gui"></a>

# components.rfid.hardware.fake\_reader\_gui.fake\_reader\_gui

<a id="components.rfid.hardware.fake_reader_gui.description"></a>

# components.rfid.hardware.fake\_reader\_gui.description

<a id="components.rfid.hardware.fake_reader_gui.gpioz_gui_addon"></a>

# components.rfid.hardware.fake\_reader\_gui.gpioz\_gui\_addon

Add GPIO input devices and output devices to the RFID Mock Reader GUI


<a id="components.rfid.hardware.fake_reader_gui.gpioz_gui_addon.create_inputs"></a>

#### create\_inputs

```python
def create_inputs(frame, default_btn_width, default_padx, default_pady)
```

Add all input devies to the GUI

**Arguments**:

- `frame`: The TK frame (e.g. LabelFrame) in the main GUI to add the buttons to

**Returns**:

List of all added GUI buttons

<a id="components.rfid.hardware.fake_reader_gui.gpioz_gui_addon.set_state"></a>

#### set\_state

```python
def set_state(value, box_state_var)
```

Change the value of a checkbox state variable


<a id="components.rfid.hardware.fake_reader_gui.gpioz_gui_addon.que_set_state"></a>

#### que\_set\_state

```python
def que_set_state(value, box_state_var)
```

Queue the action to change a checkbox state variable to the TK GUI main thread


<a id="components.rfid.hardware.fake_reader_gui.gpioz_gui_addon.fix_state"></a>

#### fix\_state

```python
def fix_state(box_state_var)
```

Prevent a checkbox state variable to change on checkbox mouse press


<a id="components.rfid.hardware.fake_reader_gui.gpioz_gui_addon.pbox_set_state"></a>

#### pbox\_set\_state

```python
def pbox_set_state(value, pbox_state_var, label_var)
```

Update progress bar state and related state label


<a id="components.rfid.hardware.fake_reader_gui.gpioz_gui_addon.que_set_pbox"></a>

#### que\_set\_pbox

```python
def que_set_pbox(value, pbox_state_var, label_var)
```

Queue the action to change the progress bar state to the TK GUI main thread


<a id="components.rfid.hardware.fake_reader_gui.gpioz_gui_addon.create_outputs"></a>

#### create\_outputs

```python
def create_outputs(frame, default_btn_width, default_padx, default_pady)
```

Add all output devices to the GUI

**Arguments**:

- `frame`: The TK frame (e.g. LabelFrame) in the main GUI to add the representations to

**Returns**:

List of all added GUI objects

<a id="components.rfid.hardware.pn532_i2c_py532.pn532_i2c_py532"></a>

# components.rfid.hardware.pn532\_i2c\_py532.pn532\_i2c\_py532

<a id="components.rfid.hardware.pn532_i2c_py532.description"></a>

# components.rfid.hardware.pn532\_i2c\_py532.description

<a id="components.rfid.hardware.rc522_spi.rc522_spi"></a>

# components.rfid.hardware.rc522\_spi.rc522\_spi

<a id="components.rfid.hardware.rc522_spi.description"></a>

# components.rfid.hardware.rc522\_spi.description

<a id="components.player"></a>

# components.player

<a id="components.player.MusicLibPath"></a>

## MusicLibPath Objects

```python
class MusicLibPath()
```

Extract the music directory from the mpd.conf file


<a id="components.player.get_music_library_path"></a>

#### get\_music\_library\_path

```python
def get_music_library_path()
```

Get the music library path


<a id="components.battery_monitor.batt_mon_i2c_ina219"></a>

# components.battery\_monitor.batt\_mon\_i2c\_ina219

<a id="components.battery_monitor.batt_mon_i2c_ina219.battmon_ina219"></a>

## battmon\_ina219 Objects

```python
class battmon_ina219(BatteryMonitorBase.BattmonBase)
```

Battery Monitor based on a INA219

See [Battery Monitor documentation](../../builders/components/power/batterymonitor.md)


<a id="components.battery_monitor.batt_mon_i2c_ads1015"></a>

# components.battery\_monitor.batt\_mon\_i2c\_ads1015

<a id="components.battery_monitor.batt_mon_i2c_ads1015.battmon_ads1015"></a>

## battmon\_ads1015 Objects

```python
class battmon_ads1015(BatteryMonitorBase.BattmonBase)
```

Battery Monitor based on a ADS1015

See [Battery Monitor documentation](../../builders/components/power/batterymonitor.md)


<a id="components.battery_monitor.batt_mon_simulator"></a>

# components.battery\_monitor.batt\_mon\_simulator

<a id="components.battery_monitor.batt_mon_simulator.battmon_simulator"></a>

## battmon\_simulator Objects

```python
class battmon_simulator(BatteryMonitorBase.BattmonBase)
```

Battery Monitor Simulator


<a id="components.battery_monitor.BatteryMonitorBase"></a>

# components.battery\_monitor.BatteryMonitorBase

<a id="components.battery_monitor.BatteryMonitorBase.pt1_frac"></a>

## pt1\_frac Objects

```python
class pt1_frac()
```

fixed point first order filter, fractional format: 2^16,2^16


<a id="components.battery_monitor.BatteryMonitorBase.BattmonBase"></a>

## BattmonBase Objects

```python
class BattmonBase()
```

Battery Monitor base class


<a id="components.battery_monitor"></a>

# components.battery\_monitor

<a id="components.controls.bluetooth_audio_buttons"></a>

# components.controls.bluetooth\_audio\_buttons

Plugin to attempt to automatically listen to it's buttons (play, next, ...)

when a bluetooth sound device (headphone, speakers) connects

This effectively does:

* register a callback with components.volume to get notified when a new sound card connects
* if that is a bluetooth device, try opening an input device with similar name using
* button listeners are run each in its own thread


<a id="components.controls.event_devices"></a>

# components.controls.event\_devices

Plugin to register event_devices (ie USB controllers, keyboards etc) in a

generic manner.

This effectively does:

    * parse the configured event devices from the evdev.yaml
    * setup listen threads


<a id="components.controls.event_devices.IS_ENABLED"></a>

#### IS\_ENABLED

Indicates that the module is enabled and loaded w/o errors


<a id="components.controls.event_devices.CONFIG_FILE"></a>

#### CONFIG\_FILE

The path of the config file the event device configuration was loaded from


<a id="components.controls.event_devices.activate"></a>

#### activate

```python
@plugin.register
def activate(device_name: str,
             button_callbacks: dict[int, Callable],
             exact: bool = True,
             mandatory_keys: set[int] | None = None)
```

Activate an event device listener

**Arguments**:

- `device_name` (`str`): device name
- `button_callbacks` (`dict[int, Callable]`): mapping of event
code to RPC
- `exact` (`bool, optional`): Should the device_name match exactly
(default, false) or be a substring of the name?
- `mandatory_keys` (`set[int] | None, optional`): Mandatory event ids the
device needs to support. Defaults to None
to require all ids from the button_callbacks

<a id="components.controls.event_devices.initialize"></a>

#### initialize

```python
@plugin.initialize
def initialize()
```

Initialize event device button listener from config

Initializes event buttons from the main configuration file.
Please see the documentation `builders/event-devices.md` for a specification of the format.


<a id="components.controls.event_devices.parse_device_config"></a>

#### parse\_device\_config

```python
def parse_device_config(config: dict) -> Tuple[str, bool, dict[int, Callable]]
```

Parse the device configuration from the config file

**Arguments**:

- `config` (`dict`): The configuration of the device

**Returns**:

`Tuple[str, bool, dict[int, Callable]]`: The parsed device configuration

<a id="components.controls.common.evdev_listener"></a>

# components.controls.common.evdev\_listener

Generalized listener for ``dev/input`` devices


<a id="components.controls.common.evdev_listener.find_device"></a>

#### find\_device

```python
def find_device(device_name: str,
                exact_name: bool = True,
                mandatory_keys: Optional[Set[int]] = None) -> str
```

Find an input device with device_name and mandatory keys.

**Arguments**:

- `device_name`: See :func:`_filter_by_device_name`
- `exact_name`: See :func:`_filter_by_device_name`
- `mandatory_keys`: See :func:`_filter_by_mandatory_keys`

**Raises**:

- `FileNotFoundError`: if no device is found.
- `AttributeError`: if device does not have the mandatory key
If multiple devices match, the first match is returned

**Returns**:

The path to the device

<a id="components.controls.common.evdev_listener.EvDevKeyListener"></a>

## EvDevKeyListener Objects

```python
class EvDevKeyListener(threading.Thread)
```

Opens and event input device from ``/dev/inputs``, and runs callbacks upon the button presses.

Input devices could be .e.g. Keyboard, Bluetooth audio buttons, USB buttons

Runs as a separate thread. When device disconnects or disappears, thread exists. A new thread must be started
when device re-connects.

Assign callbacks to :attr:`EvDevKeyListener.button_callbacks`


<a id="components.controls.common.evdev_listener.EvDevKeyListener.__init__"></a>

#### \_\_init\_\_

```python
def __init__(device_name_request: str, exact_name: bool, thread_name: str)
```

**Arguments**:

- `device_name_request`: The device name to look for
- `exact_name`: If true, device_name must mach exactly, else a match is returned if device_name is a substring of
the reported device name
- `thread_name`: Name of the listener thread

<a id="components.controls.common.evdev_listener.EvDevKeyListener.run"></a>

#### run

```python
def run()
```



<a id="components.controls.common.evdev_listener.EvDevKeyListener.start"></a>

#### start

```python
def start() -> None
```

Start the tread and start listening


<a id="components.controls"></a>

# components.controls

<a id="components.misc"></a>

# components.misc

Miscellaneous function package


<a id="components.misc.rpc_cmd_help"></a>

#### rpc\_cmd\_help

```python
@plugin.register
def rpc_cmd_help()
```

Return all commands for RPC


<a id="components.misc.get_all_loaded_packages"></a>

#### get\_all\_loaded\_packages

```python
@plugin.register
def get_all_loaded_packages()
```

Get all successfully loaded plugins


<a id="components.misc.get_all_failed_packages"></a>

#### get\_all\_failed\_packages

```python
@plugin.register
def get_all_failed_packages()
```

Get all plugins with error during load or initialization


<a id="components.misc.get_start_time"></a>

#### get\_start\_time

```python
@plugin.register
def get_start_time()
```

Time when JukeBox has been started


<a id="components.misc.get_log"></a>

#### get\_log

```python
def get_log(handler_name: str)
```

Get the log file from the loggers (debug_file_handler, error_file_handler)


<a id="components.misc.get_log_debug"></a>

#### get\_log\_debug

```python
@plugin.register
def get_log_debug()
```

Get the log file (from the debug_file_handler)


<a id="components.misc.get_log_error"></a>

#### get\_log\_error

```python
@plugin.register
def get_log_error()
```

Get the log file (from the error_file_handler)


<a id="components.misc.get_git_state"></a>

#### get\_git\_state

```python
@plugin.register
def get_git_state()
```

Return git state information for the current branch


<a id="components.misc.empty_rpc_call"></a>

#### empty\_rpc\_call

```python
@plugin.register
def empty_rpc_call(msg: str = '')
```

This function does nothing.

The RPC command alias 'none' is mapped to this function.

This is also used when configuration errors lead to non existing RPC command alias definitions.
When the alias definition is void, we still want to return a valid function to simplify error handling
up the module call stack.

**Arguments**:

- `msg`: If present, this message is send to the logger with severity warning

<a id="components.misc.get_app_settings"></a>

#### get\_app\_settings

```python
@plugin.register
def get_app_settings()
```

Return settings for web app stored in jukebox.yaml


<a id="components.misc.set_app_settings"></a>

#### set\_app\_settings

```python
@plugin.register
def set_app_settings(settings={})
```

Set configuration settings for the web app.


<a id="components.publishing"></a>

# components.publishing

Plugin interface for Jukebox Publisher

Thin wrapper around jukebox.publishing to benefit from the plugin loading / exit handling / function handling

This is the first package to be loaded and the last to be closed: put Hello and Goodbye publish messages here.


<a id="components.publishing.republish"></a>

#### republish

```python
@plugin.register
def republish(topic=None)
```

Re-publish the topic tree 'topic' to all subscribers

**Arguments**:

- `topic`: Topic tree to republish. None = resend all

<a id="jukebox"></a>

# jukebox

<a id="jukebox.callingback"></a>

# jukebox.callingback

Provides a generic callback handler


<a id="jukebox.callingback.CallbackHandler"></a>

## CallbackHandler Objects

```python
class CallbackHandler()
```

Generic Callback Handler to collect callbacks functions through :func:`register` and execute them

with :func:`run_callbacks`

A lock is used to sequence registering of new functions and running callbacks.

**Arguments**:

- `name`: A name of this handler for usage in log messages
- `logger`: The logger instance to use for logging
- `context`: A custom context handler to use as lock. If none, a local :class:`threading.Lock()` will be created

<a id="jukebox.callingback.CallbackHandler.register"></a>

#### register

```python
def register(func: Optional[Callable[..., None]])
```

Register a new function to be executed when the callback event happens

**Arguments**:

- `func`: The function to register. If set to :data:`None`, this register request is silently ignored.

<a id="jukebox.callingback.CallbackHandler.run_callbacks"></a>

#### run\_callbacks

```python
def run_callbacks(*args, **kwargs)
```

Run all registered callbacks.

*ALL* exceptions from callback functions will be caught and logged only.
Exceptions are not raised upwards!


<a id="jukebox.callingback.CallbackHandler.has_callbacks"></a>

#### has\_callbacks

```python
@property
def has_callbacks()
```



<a id="jukebox.plugs"></a>

# jukebox.plugs

A plugin package with some special functionality

Plugins packages are python packages that are dynamically loaded. From these packages only a subset of objects is exposed
through the plugs.call interface. The python packages can use decorators or dynamic function call to register (callable)
objects.

The python package name may be different from the name the package is registered under in plugs. This allows to load different
python packages for a specific feature based on a configuration file. Note: Python package are still loaded as regular
python packages and can be accessed by normal means

If you want to provide additional functionality to the same feature (probably even for run-time switching)
you can implement a Factory Pattern using this package. Take a look at volume.py as an example.

**Example:** Decorate a function for auto-registering under it's own name:

    import jukebox.plugs as plugs
    @plugs.register
    def func1(param):
        pass

**Example:** Decorate a function for auto-registering under a new name:

    @plugs.register(name='better_name')
    def func2(param):
        pass

**Example:** Register a function during run-time under it's own name:

    def func3(param):
        pass
    plugs.register(func3)

**Example:** Register a function during run-time under a new name:

    def func4(param):
        pass
    plugs.register(func4, name='other_name', package='other_package')

**Example:** Decorate a class for auto registering during initialization,
including all methods (see _register_class for more info):

    @plugs.register(auto_tag=True)
    class MyClass1:
        pass

**Example:** Register a class instance, from which only report is a callable method through the plugs interface:

    class MyClass2:
        @plugs.tag
        def report(self):
            pass
    myinst2 = MyClass2()
    plugin.register(myinst2, name='myinst2')

Naming convention:

* package
  * Either a python package
  * or a plugin package (which is the python package but probably loaded under a different name inside plugs)
* plugin
  * An object from the package that can be accessed through the plugs call function (i.e. a function or a class instance)
  * The string name to above object
* name
  * The string name of the plugin object for registration
* method
  * In case the object is a class instance a bound method to call from the class instance
  * The string name to above object


<a id="jukebox.plugs.PluginPackageClass"></a>

## PluginPackageClass Objects

```python
class PluginPackageClass()
```

A local data class for holding all information about a loaded plugin package


<a id="jukebox.plugs.register"></a>

#### register

```python
@overload
def register(plugin: Callable) -> Callable
```

1-level decorator around a function


<a id="jukebox.plugs.register"></a>

#### register

```python
@overload
def register(plugin: Type) -> Any
```

Signature: 1-level decorator around a class


<a id="jukebox.plugs.register"></a>

#### register

```python
@overload
def register(*, name: str, package: Optional[str] = None) -> Callable
```

Signature: 2-level decorator around a function


<a id="jukebox.plugs.register"></a>

#### register

```python
@overload
def register(*, auto_tag: bool = False, package: Optional[str] = None) -> Type
```

Signature: 2-level decorator around a class


<a id="jukebox.plugs.register"></a>

#### register

```python
@overload
def register(plugin: Callable[..., Any] = None,
             *,
             name: Optional[str] = None,
             package: Optional[str] = None,
             replace: bool = False) -> Callable
```

Signature: Run-time registration of function / class instance / bound method


<a id="jukebox.plugs.register"></a>

#### register

```python
def register(plugin: Optional[Callable] = None,
             *,
             name: Optional[str] = None,
             package: Optional[str] = None,
             replace: bool = False,
             auto_tag: bool = False) -> Callable
```

A generic decorator / run-time function to register plugin module callables

The functions comes in five distinct signatures for 5 use cases:

1. ``@plugs.register``: decorator for a class w/o any arguments
2. ``@plugs.register``: decorator for a function w/o any arguments
3. ``@plugs.register(auto_tag=bool)``: decorator for a class with 1 arguments
4. ``@plugs.register(name=name, package=package)``: decorator for a function with 1 or 2 arguments
5. ``plugs.register(plugin, name=name, package=package)``: run-time registration of
    * function
    * bound method
    * class instance

For more documentation see the functions
* :func:`_register_obj`
* :func:`_register_class`

See the examples in Module :mod:`plugs` how to use this decorator / function

**Arguments**:

- `plugin`: 
- `name`: 
- `package`: 
- `replace`: 
- `auto_tag`: 

<a id="jukebox.plugs.tag"></a>

#### tag

```python
def tag(func: Callable) -> Callable
```

Method decorator for tagging a method as callable through the plugs interface

Note that the instantiated class must still be registered as plugin object
(either with the class decorator or dynamically)

**Arguments**:

- `func`: function to decorate

**Returns**:

the function

<a id="jukebox.plugs.initialize"></a>

#### initialize

```python
def initialize(func: Callable) -> Callable
```

Decorator for functions that shall be called by the plugs package directly after the module is loaded

**Arguments**:

- `func`: Function to decorate

**Returns**:

The function itself

<a id="jukebox.plugs.finalize"></a>

#### finalize

```python
def finalize(func: Callable) -> Callable
```

Decorator for functions that shall be called by the plugs package directly after ALL modules are loaded

**Arguments**:

- `func`: Function to decorate

**Returns**:

The function itself

<a id="jukebox.plugs.atexit"></a>

#### atexit

```python
def atexit(func: Callable[[int], Any]) -> Callable[[int], Any]
```

Decorator for functions that shall be called by the plugs package directly after at exit of program.

> [!IMPORTANT]
> There is no automatism as in atexit.atexit. The function plugs.shutdown() must be explicitly called
> during the shutdown procedure of your program. This is by design, so you can choose the exact situation in your
> shutdown handler.

The atexit-functions are called with a single integer argument, which is passed down from plugin.exit(int)
It is intended for passing down the signal number that initiated the program termination

**Arguments**:

- `func`: Function to decorate

**Returns**:

The function itself

<a id="jukebox.plugs.load"></a>

#### load

```python
def load(package: str,
         load_as: Optional[str] = None,
         prefix: Optional[str] = None)
```

Loads a python package as plugin package

Executes a regular python package load. That means a potentially existing `__init__.py` is executed.
Decorator `@register` can by used to register functions / classes / class istances as plugin callable
Decorator `@initializer` can be used to tag functions that shall be called after package loading
Decorator `@finalizer` can be used to tag functions that shall be called after ALL plugin packges have been loaded
Instead of using `@initializer`, you may of course use `__init__.py`

Python packages may be loaded under a different plugs package name. Python packages must be unique and the name under
which they are loaded as plugin package also.

**Arguments**:

- `package`: Python package to load as plugin package
- `load_as`: Plugin package registration name. If None the name is the python's package simple name
- `prefix`: Prefix to python package to create fully qualified name. This is used only to locate the python package
and ignored otherwise. Useful if all the plugin module are in a dedicated folder

<a id="jukebox.plugs.load_all_named"></a>

#### load\_all\_named

```python
def load_all_named(packages_named: Mapping[str, str],
                   prefix: Optional[str] = None,
                   ignore_errors=False)
```

Load all packages in packages_named with mapped names

**Arguments**:

- `packages_named`: Dict[load_as, package]

<a id="jukebox.plugs.load_all_unnamed"></a>

#### load\_all\_unnamed

```python
def load_all_unnamed(packages_unnamed: Iterable[str],
                     prefix: Optional[str] = None,
                     ignore_errors=False)
```

Load all packages in packages_unnamed with default names


<a id="jukebox.plugs.load_all_finalize"></a>

#### load\_all\_finalize

```python
def load_all_finalize(ignore_errors=False)
```

Calls all functions registered with @finalize from all loaded modules in the order they were loaded

This must be executed after the last plugin package is loaded


<a id="jukebox.plugs.close_down"></a>

#### close\_down

```python
def close_down(**kwargs) -> Any
```

Calls all functions registered with @atexit from all loaded modules in reverse order of module load order

Modules are processed in reverse order. Several at-exit tagged functions of a single module are processed
in the order of registration.

Errors raised in functions are suppressed to ensure all plugins are processed


<a id="jukebox.plugs.call"></a>

#### call

```python
def call(package: str,
         plugin: str,
         method: Optional[str] = None,
         *,
         args=(),
         kwargs=None,
         as_thread: bool = False,
         thread_name: Optional[str] = None) -> Any
```

Call a function/method from the loaded plugins

If a plugin is a function or a callable instance of a class, this is equivalent to

``package.plugin(*args, **kwargs)``

If plugin is a class instance from which a method is called, this is equivalent to the followig.
Also remember, that method must have the attribute ``plugin_callable = True``

``package.plugin.method(*args, **kwargs)``

Calls are serialized by a thread lock. The thread lock is shared with call_ignore_errors.

> [!NOTE]
> There is no logger in this function as they all belong up-level where the exceptions are handled.
> If you want logger messages instead of exceptions, use :func:`call_ignore_errors`

**Arguments**:

- `package`: Name of the plugin package in which to look for function/class instance
- `plugin`: Function name or instance name of a class
- `method`: Method name when accessing a class instance' method. Leave at *None* if unneeded.
- `as_thread`: Run the callable in separate daemon thread.
There is no return value from the callable in this case! The return value is the thread object.
Also note that Exceptions in the Thread must be handled in the Thread and are not propagated to the main Thread.
All threads are started as daemon threads with terminate upon main program termination.
There is not stop-thread mechanism. This is intended for short lived threads.
- `thread_name`: Name of the thread
- `args`: Arguments passed to callable
- `kwargs`: Keyword arguments passed to callable

**Returns**:

The return value from the called function, or, if started as thread the thread object

<a id="jukebox.plugs.call_ignore_errors"></a>

#### call\_ignore\_errors

```python
def call_ignore_errors(package: str,
                       plugin: str,
                       method: Optional[str] = None,
                       *,
                       args=(),
                       kwargs=None,
                       as_thread: bool = False,
                       thread_name: Optional[str] = None) -> Any
```

Call a function/method from the loaded plugins ignoring all raised Exceptions.

Errors get logged.

See :func:`call` for parameter documentation.


<a id="jukebox.plugs.exists"></a>

#### exists

```python
def exists(package: str,
           plugin: Optional[str] = None,
           method: Optional[str] = None) -> bool
```

Check if an object is registered within the plugs package


<a id="jukebox.plugs.get"></a>

#### get

```python
def get(package: str,
        plugin: Optional[str] = None,
        method: Optional[str] = None) -> Any
```

Get a plugs-package registered object

The return object depends on the number of parameters

* 1 argument: Get the python module reference for the plugs *package*
* 2 arguments: Get the plugin reference for the plugs *package.plugin*
* 3 arguments: Get the plugin reference for the plugs *package.plugin.method*


<a id="jukebox.plugs.loaded_as"></a>

#### loaded\_as

```python
def loaded_as(module_name: str) -> str
```

Return the plugin name a python module is loaded as


<a id="jukebox.plugs.delete"></a>

#### delete

```python
def delete(package: str, plugin: Optional[str] = None, ignore_errors=False)
```

Delete a plugin object from the registered plugs callables

> [!NOTE]
> This does not 'unload' the python module. It merely makes it un-callable via plugs!


<a id="jukebox.plugs.dump_plugins"></a>

#### dump\_plugins

```python
def dump_plugins(stream)
```

Write a human readable summary of all plugin callables to stream


<a id="jukebox.plugs.summarize"></a>

#### summarize

```python
def summarize()
```

Create a reference summary of all plugin callables in dictionary format


<a id="jukebox.plugs.generate_help_rst"></a>

#### generate\_help\_rst

```python
def generate_help_rst(stream)
```

Write a reference of all plugin callables in Restructured Text format


<a id="jukebox.plugs.get_all_loaded_packages"></a>

#### get\_all\_loaded\_packages

```python
def get_all_loaded_packages() -> Dict[str, str]
```

Report a short summary of all loaded packages

**Returns**:

Dictionary of the form `{loaded_as: loaded_from, ...}`

<a id="jukebox.plugs.get_all_failed_packages"></a>

#### get\_all\_failed\_packages

```python
def get_all_failed_packages() -> Dict[str, str]
```

Report those packages that did not load error free

> [!NOTE]
> Package could fail to load
> * altogether: these package are not registered
> * partially: during initializer, finalizer functions: The package is loaded,
> but the function did not execute error-free
>
> Partially loaded packages are listed in both _PLUGINS and _PLUGINS_FAILED

**Returns**:

Dictionary of the form `{loaded_as: loaded_from, ...}`

<a id="jukebox.cfghandler"></a>

# jukebox.cfghandler

This module handles global and local configuration data

The concept is that config handler is created and initialized once in the main thread::

    cfg = get_handler('global')
    load_yaml(cfg, 'filename.yaml')

In all other modules (in potentially different threads) the same handler is obtained and used by::

    cfg = get_handler('global')

This eliminates the need to pass an effectively global configuration handler by parameters across the entire design.
Handlers are identified by their name (in the above example *global*)

The function :func:`get_handler` is the main entry point to obtain a new or existing handler.


<a id="jukebox.cfghandler.ConfigHandler"></a>

## ConfigHandler Objects

```python
class ConfigHandler()
```

The configuration handler class

Don't instantiate directly. Always use :func:`get_handler`!

**Threads:**

All threads can read and write to the configuration data.
**Proper thread-safeness must be ensured** by the the thread modifying the data by acquiring the lock
Easiest and best way is to use the context handler::

    with cfg:
       cfg['key'] = 66
       cfg.setndefault('hello', value='world')

For a single function call, this is done implicitly. In this case, there is no need
to explicitly acquire the lock.

Alternatively, you can lock and release manually by using :func:`acquire` and :func:`release`
But be very sure to release the lock even in cases of errors an exceptions!
Else we have a deadlock.

Reading may be done without acquiring a lock. But be aware that when reading multiple values without locking, another
thread may intervene and modify some values in between! So, locking is still recommended.


<a id="jukebox.cfghandler.ConfigHandler.loaded_from"></a>

#### loaded\_from

```python
@property
def loaded_from() -> Optional[str]
```

Property to store filename from which the config was loaded


<a id="jukebox.cfghandler.ConfigHandler.get"></a>

#### get

```python
def get(key, *, default=None)
```

Enforce keyword on default to avoid accidental misuse when actually getn is wanted


<a id="jukebox.cfghandler.ConfigHandler.setdefault"></a>

#### setdefault

```python
def setdefault(key, *, value)
```

Enforce keyword on default to avoid accidental misuse when actually setndefault is wanted


<a id="jukebox.cfghandler.ConfigHandler.getn"></a>

#### getn

```python
def getn(*keys, default=None)
```

Get the value at arbitrary hierarchy depth. Return ``default`` if key not present

The *default* value is returned no matter at which hierarchy level the path aborts.
A hierarchy is considered as any type with a :func:`get` method.


<a id="jukebox.cfghandler.ConfigHandler.setn"></a>

#### setn

```python
def setn(*keys, value, hierarchy_type=None) -> None
```

Set the ``key: value`` pair at arbitrary hierarchy depth

All non-existing hierarchy levels are created.

**Arguments**:

- `keys`: Key hierarchy path through the nested levels
- `value`: The value to set
- `hierarchy_type`: The type for new hierarchy levels. If *None*, the top-level type
is used

<a id="jukebox.cfghandler.ConfigHandler.setndefault"></a>

#### setndefault

```python
def setndefault(*keys, value, hierarchy_type=None)
```

Set the ``key: value`` pair at arbitrary hierarchy depth unless the key already exists

All non-existing hierarchy levels are created.

**Arguments**:

- `keys`: Key hierarchy path through the nested levels
- `value`: The default value to set
- `hierarchy_type`: The type for new hierarchy levels. If *None*, the top-level type
is used

**Returns**:

The actual value or or the default value if key does not exit

<a id="jukebox.cfghandler.ConfigHandler.config_dict"></a>

#### config\_dict

```python
def config_dict(data)
```

Initialize configuration data from dict-like data structure

**Arguments**:

- `data`: configuration data

<a id="jukebox.cfghandler.ConfigHandler.is_modified"></a>

#### is\_modified

```python
def is_modified() -> bool
```

Check if the data has changed since the last load/store

> [!NOTE]
> This relies on the *__str__* representation of the underlying data structure
> In case of ruamel, this ignores comments and only looks at the data


<a id="jukebox.cfghandler.ConfigHandler.clear_modified"></a>

#### clear\_modified

```python
def clear_modified() -> None
```

Sets the current state as new baseline, clearing the is_modified state


<a id="jukebox.cfghandler.ConfigHandler.save"></a>

#### save

```python
def save(only_if_changed: bool = False) -> None
```

Save config back to the file it was loaded from

If you want to save to a different file, use :func:`write_yaml`.


<a id="jukebox.cfghandler.ConfigHandler.load"></a>

#### load

```python
def load(filename: str) -> None
```

Load YAML config file into memory


<a id="jukebox.cfghandler.get_handler"></a>

#### get\_handler

```python
def get_handler(name: str) -> ConfigHandler
```

Get a configuration data handler with the specified name, creating it

if it doesn't yet exit. If created, it is always created empty.

This is the main entry point for obtaining an configuration handler

**Arguments**:

- `name`: Name of the config handler

**Returns**:

`ConfigHandler`: The configuration data handler for *name*

<a id="jukebox.cfghandler.load_yaml"></a>

#### load\_yaml

```python
def load_yaml(cfg: ConfigHandler, filename: str) -> None
```

Load a yaml file into a ConfigHandler

**Arguments**:

- `cfg`: ConfigHandler instance
- `filename`: filename to yaml file

**Returns**:

None

<a id="jukebox.cfghandler.write_yaml"></a>

#### write\_yaml

```python
def write_yaml(cfg: ConfigHandler,
               filename: str,
               only_if_changed: bool = False,
               *args,
               **kwargs) -> None
```

Writes ConfigHandler data to yaml file / sys.stdout

**Arguments**:

- `cfg`: ConfigHandler instance
- `filename`: filename to output file. If *sys.stdout*, output is written to console
- `only_if_changed`: Write file only, if ConfigHandler.is_modified()
- `args`: passed on to yaml.dump(...)
- `kwargs`: passed on to yaml.dump(...)

**Returns**:

None

<a id="jukebox.speaking_text"></a>

# jukebox.speaking\_text

Text to Speech. Plugin to speak any given text via speaker


<a id="jukebox.utils"></a>

# jukebox.utils

Common utility functions


<a id="jukebox.utils.decode_rpc_call"></a>

#### decode\_rpc\_call

```python
def decode_rpc_call(cfg_rpc_call: Dict) -> Optional[Dict]
```

Makes sure that the core rpc call parameters have valid default values in cfg_rpc_call.

> [!IMPORTANT]
> Leaves all other parameters in cfg_action untouched or later downstream processing!

**Arguments**:

- `cfg_rpc_call`: RPC command as configuration entry

**Returns**:

A fully populated deep copy of cfg_rpc_call

<a id="jukebox.utils.decode_rpc_command"></a>

#### decode\_rpc\_command

```python
def decode_rpc_command(cfg_rpc_cmd: Dict,
                       logger: logging.Logger = log) -> Optional[Dict]
```

Decode an RPC Command from a config entry.

This means

* Decode RPC command alias (if present)
* Ensure all RPC call parameters have valid default values

If the command alias cannot be decoded correctly, the command is mapped to misc.empty_rpc_call
which emits a misuse warning when called
If an explicitly specified this is not done. However, it is ensured that the returned
dictionary contains all mandatory parameters for an RPC call. RPC call functions have error handling
for non-existing RPC commands and we get a clearer error message.

**Arguments**:

- `cfg_rpc_cmd`: RPC command as configuration entry
- `logger`: The logger to use

**Returns**:

A decoded, fully populated deep copy of cfg_rpc_cmd

<a id="jukebox.utils.decode_and_call_rpc_command"></a>

#### decode\_and\_call\_rpc\_command

```python
def decode_and_call_rpc_command(rpc_cmd: Dict, logger: logging.Logger = log)
```

Convenience function combining decode_rpc_command and plugs.call_ignore_errors


<a id="jukebox.utils.bind_rpc_command"></a>

#### bind\_rpc\_command

```python
def bind_rpc_command(cfg_rpc_cmd: Dict,
                     dereference=False,
                     logger: logging.Logger = log)
```

Decode an RPC command configuration entry and bind it to a function

**Arguments**:

- `dereference`: Dereference even the call to plugs.call(...)
    ``. If false, the returned function is ``plugs.call(package, plugin, method, *args, **kwargs)`` with
        all checks applied at bind time
    ``. If true, the returned function is ``package.plugin.method(*args, **kwargs)`` with
        all checks applied at bind time.

Setting deference to True, circumvents the dynamic nature of the plugins: the function to call
    must exist at bind time and cannot change. If False, the function to call must only exist at call time.
    This can be important during the initialization where package ordering and initialization means that not all
    classes have been instantiated yet. With dereference=True also the plugs thread lock for serialization of calls
    is circumvented. Use with care!

**Returns**:

Callable function w/o parameters which directly runs the RPC command
using plugs.call_ignore_errors

<a id="jukebox.utils.rpc_call_to_str"></a>

#### rpc\_call\_to\_str

```python
def rpc_call_to_str(cfg_rpc_call: Dict, with_args=True) -> str
```

Return a readable string of an RPC call config

**Arguments**:

- `cfg_rpc_call`: RPC call configuration entry
- `with_args`: Return string shall include the arguments of the function

<a id="jukebox.utils.get_config_action"></a>

#### get\_config\_action

```python
def get_config_action(cfg, section, option, default, valid_actions_dict,
                      logger)
```

Looks up the given {section}.{option} config option and returns

the associated entry from valid_actions_dict, if valid. Falls back to the given
default otherwise.


<a id="jukebox.utils.generate_cmd_alias_rst"></a>

#### generate\_cmd\_alias\_rst

```python
def generate_cmd_alias_rst(stream)
```

Write a reference of all rpc command aliases in Restructured Text format


<a id="jukebox.utils.generate_cmd_alias_reference"></a>

#### generate\_cmd\_alias\_reference

```python
def generate_cmd_alias_reference(stream)
```

Write a reference of all rpc command aliases in text format


<a id="jukebox.utils.get_git_state"></a>

#### get\_git\_state

```python
def get_git_state()
```

Return git state information for the current branch


<a id="jukebox.version"></a>

# jukebox.version

<a id="jukebox.version.version"></a>

#### version

```python
def version()
```

Return the Jukebox version as a string


<a id="jukebox.version.version_info"></a>

#### version\_info

```python
def version_info()
```

Return the Jukebox version as a tuple of three numbers

If this is a development version, an identifier string will be appended after the third integer.


<a id="jukebox.playlistgenerator"></a>

# jukebox.playlistgenerator

Playlists are build from directory content in the following way:

a directory is parsed and files are added to the playlist in the following way

1. files are added in alphabetic order
2. files ending with ``*livestream.txt`` are unpacked and the containing URL(s) are added verbatim to the playlist
3. files ending with ``*podcast.txt`` are unpacked and the containing Podcast URL(s) are expanded and added to the playlist
4. files ending with ``*.m3u`` are treated as folder playlist. Regular folder processing is suspended and the playlist
   is build solely from the ``*.m3u`` content. Only the alphabetically first ``*.m3u`` is processed. URLs are added verbatim
   to the playlist except for ``*.xml`` and ``*.podcast`` URLS, which are expanded first

An directory may contain a mixed set of files and multiple ``*.txt`` files, e.g.

    01-livestream.txt
    02-livestream.txt
    music.mp3
    podcast.txt

All files are treated as music files and are added to the playlist, except those:

 * starting with ``.``,
 * not having a file ending, i.e. do not contain a ``.``,
 * ending with ``.txt``,
 * ending with ``.m3u``,
 * ending with one of the excluded file endings in :attr:`PlaylistCollector._exclude_endings`

In recursive mode, the playlist is generated by concatenating all sub-folder playlists. Sub-folders are parsed
in alphabetic order. Symbolic links are being followed. The above rules are enforced on a per-folder bases.
This means, one ``*.m3u`` file per sub-folder is processed (if present).

In ``*.txt`` and ``*.m3u`` files, all lines starting with ``#`` are ignored.


<a id="jukebox.playlistgenerator.TYPE_DECODE"></a>

#### TYPE\_DECODE

Types if file entires in parsed directory


<a id="jukebox.playlistgenerator.PlaylistCollector"></a>

## PlaylistCollector Objects

```python
class PlaylistCollector()
```

Build a playlist from directory(s)

This class is intended to be used with an absolute path to the music library::

    plc = PlaylistCollector('/home/chris/music')
    plc.parse('Traumfaenger')
    print(f"res = {plc}")

But it can also be used with relative paths from current working directory::

    plc = PlaylistCollector('.')
    plc.parse('../../../../music/Traumfaenger')
    print(f"res = {plc}")

The file ending exclusion list :attr:`PlaylistCollector._exclude_endings` is a class variable for performance reasons.
If changed it will affect all instances. For modifications always call :func:`set_exclusion_endings`.


<a id="jukebox.playlistgenerator.PlaylistCollector.__init__"></a>

#### \_\_init\_\_

```python
def __init__(music_library_base_path='/')
```

Initialize the playlist generator with music_library_base_path

**Arguments**:

- `music_library_base_path`: Base path the the music library. This is used to locate the file in the disk
but is omitted when generating the playlist entries. I.e. all files in the playlist are relative to this base dir

<a id="jukebox.playlistgenerator.PlaylistCollector.set_exclusion_endings"></a>

#### set\_exclusion\_endings

```python
@classmethod
def set_exclusion_endings(cls, endings: List[str])
```

Set the class-wide file ending exclusion list

See :attr:`PlaylistCollector._exclude_endings`


<a id="jukebox.playlistgenerator.PlaylistCollector.get_directory_content"></a>

#### get\_directory\_content

```python
def get_directory_content(path='.')
```

Parse the folder ``path`` and create a content list. Depth is always the current level

**Arguments**:

- `path`: Path to folder **relative** to ``music_library_base_path``

**Returns**:

[ { type: 'directory', name: 'Simone', path: '/some/path/to/Simone' }, {...} ]
where type is one of :attr:`TYPE_DECODE`

<a id="jukebox.playlistgenerator.PlaylistCollector.parse"></a>

#### parse

```python
def parse(path='.', recursive=False)
```

Parse the folder ``path`` and create a playlist from its content

**Arguments**:

- `path`: Path to folder **relative** to ``music_library_base_path``
- `recursive`: Parse folder recursivley, or stay in top-level folder

<a id="jukebox.multitimer"></a>

# jukebox.multitimer

Multitimer Module


<a id="jukebox.multitimer.MultiTimer"></a>

## MultiTimer Objects

```python
class MultiTimer(threading.Thread)
```

Call a function after a specified number of seconds, repeat that iteration times

May be cancelled during any of the wait times.
Function is called with keyword parameter 'iteration' (which decreases down to 0 for the last iteration)

If iterations is negative, an endlessly repeating timer is created (which needs to be cancelled with cancel())

Initiates start and publishing by calling self.publish_callback

Note: Inspired by threading.Timer and generally using the same API


<a id="jukebox.multitimer.MultiTimer.cancel"></a>

#### cancel

```python
def cancel()
```

Stop the timer if it hasn't finished all iterations yet.


<a id="jukebox.multitimer.GenericTimerClass"></a>

## GenericTimerClass Objects

```python
class GenericTimerClass()
```

Interface for plugin / RPC accessibility for a single event timer


<a id="jukebox.multitimer.GenericTimerClass.__init__"></a>

#### \_\_init\_\_

```python
def __init__(name, wait_seconds: float, function, args=None, kwargs=None)
```

**Arguments**:

- `wait_seconds`: The time in seconds to wait before calling function
- `function`: The function to call with args and kwargs.
- `args`: Parameters for function call
- `kwargs`: Parameters for function call

<a id="jukebox.multitimer.GenericTimerClass.start"></a>

#### start

```python
@plugin.tag
def start(wait_seconds=None)
```

Start the timer (with default or new parameters)


<a id="jukebox.multitimer.GenericTimerClass.cancel"></a>

#### cancel

```python
@plugin.tag
def cancel()
```

Cancel the timer


<a id="jukebox.multitimer.GenericTimerClass.toggle"></a>

#### toggle

```python
@plugin.tag
def toggle()
```

Toggle the activation of the timer


<a id="jukebox.multitimer.GenericTimerClass.trigger"></a>

#### trigger

```python
@plugin.tag
def trigger()
```

Trigger the next target execution before the time is up


<a id="jukebox.multitimer.GenericTimerClass.is_alive"></a>

#### is\_alive

```python
@plugin.tag
def is_alive()
```

Check if timer is active


<a id="jukebox.multitimer.GenericTimerClass.get_timeout"></a>

#### get\_timeout

```python
@plugin.tag
def get_timeout()
```

Get the configured time-out

**Returns**:

The total wait time. (Not the remaining wait time!)

<a id="jukebox.multitimer.GenericTimerClass.set_timeout"></a>

#### set\_timeout

```python
@plugin.tag
def set_timeout(wait_seconds: float)
```

Set a new time-out in seconds. Re-starts the timer if already running!


<a id="jukebox.multitimer.GenericTimerClass.publish"></a>

#### publish

```python
@plugin.tag
def publish()
```

Publish the current state and config


<a id="jukebox.multitimer.GenericTimerClass.get_state"></a>

#### get\_state

```python
@plugin.tag
def get_state()
```

Get the current state and config as dictionary


<a id="jukebox.multitimer.GenericEndlessTimerClass"></a>

## GenericEndlessTimerClass Objects

```python
class GenericEndlessTimerClass(GenericTimerClass)
```

Interface for plugin / RPC accessibility for an event timer call function endlessly every m seconds


<a id="jukebox.multitimer.GenericMultiTimerClass"></a>

## GenericMultiTimerClass Objects

```python
class GenericMultiTimerClass(GenericTimerClass)
```

Interface for plugin / RPC accessibility for an event timer that performs an action n times every m seconds


<a id="jukebox.multitimer.GenericMultiTimerClass.__init__"></a>

#### \_\_init\_\_

```python
def __init__(name,
             iterations: int,
             wait_seconds_per_iteration: float,
             callee,
             args=None,
             kwargs=None)
```

**Arguments**:

- `iterations`: Number of times callee is called
- `wait_seconds_per_iteration`: Wait in seconds before each iteration
- `callee`: A builder class that gets instantiated once as callee(*args, iterations=iterations, **kwargs).
Then with every time out iteration __call__(*args, iteration=iteration, **kwargs) is called.
'iteration' is the current iteration count in decreasing order!
- `args`: 
- `kwargs`: 

<a id="jukebox.multitimer.GenericMultiTimerClass.start"></a>

#### start

```python
@plugin.tag
def start(iterations=None, wait_seconds_per_iteration=None)
```

Start the timer (with default or new parameters)


<a id="jukebox.NvManager"></a>

# jukebox.NvManager

<a id="jukebox.publishing.subscriber"></a>

# jukebox.publishing.subscriber

<a id="jukebox.publishing"></a>

# jukebox.publishing

<a id="jukebox.publishing.get_publisher"></a>

#### get\_publisher

```python
def get_publisher()
```

Return the publisher instance for this thread

Per thread, only one publisher instance is required to connect to the inproc socket.
A new instance is created if it does not already exist.

If there is a remote-chance that your function publishing something may be called form
different threads, always make a fresh call to ``get_publisher()`` to get the correct instance for the current thread.

Example::

    import jukebox.publishing as publishing

    class MyClass:
        def __init__(self):
            pass

        def say_hello(name):
            publishing.get_publisher().send('hello', f'Hi {name}, howya?')

To stress what **NOT** to do: don't get a publisher instance in the constructor and save it to ``self._pub``.
If you do and ``say_hello`` gets called from different threads, the publisher of the thread which instantiated the class
will be used.

If you need your very own private Publisher Instance, you'll need to instantiate it yourself.
But: the use cases are very rare for that. I cannot think of one at the moment.

**Remember**: Don’t share ZeroMQ sockets between threads.


<a id="jukebox.publishing.server"></a>

# jukebox.publishing.server

## Publishing Server

The common publishing server for the entire Jukebox using ZeroMQ

### Structure

    +-----------------------+
    |  functional interface |   Publisher
    |                       |     - functional interface for single Thread
    |        PUB            |     - sends data to publisher (and thus across threads)
    +-----------------------+
              | (1)
              v
    +-----------------------+
    |        SUB (bind)     |   PublishServer
    |                       |     - Last Value (LV) Cache
    |        XPUB (bind)    |     - Subscriber notification and LV resend
    +-----------------------+     - independent thread
              | (2)
              v

#### Connection (1): Internal connection

Internal connection only - do not use (no, not even inside this App for you own plugins - always bind to the PublishServer)

    Protocol: Multi-part message

    Part 1: Topic (in topic tree format)
        E.g. player.status.elapsed

    Part 2: Payload or Message in json serialization
        If empty (i.e. ``b''``), it means delete the topic sub-tree from cache. And instruct subscribers to do the same

    Part 3: Command
        Usually empty, i.e. ``b''``. If not empty the message is treated as command for the PublishServer
        and the message is not forwarded to the outside. This third part of the message is never forwarded

#### Connection (2): External connection

Upon connection of a new subscriber, the entire current state is resend from cache to ALL subscribers!
Subscribers must subscribe to topics. Topics are treated as topic trees! Subscribing to a root tree will
also get you all the branch topics. To get everything, subscribe to ``b''``

    Protocol: Multi-part message

    Part 1: Topic (in topic tree format)
        E.g. player.status.elapsed

    Part 2: Payload or Message in json serialization
        If empty (i.e. b''), it means the subscriber must delete this key locally (not valid anymore)

### Why? Why?

Check out the [ZeroMQ Documentation](https://zguide.zeromq.org/docs/chapter5)
for why you need a proxy in a good design.

For use case, we made a few simplifications

### Design Rationales

* "If you need [millions of messages per second](https://zguide.zeromq.org/docs/chapter5/`Pros`-and-Cons-of-Pub-Sub)
  sent to thousands of points,
  you'll appreciate pub-sub a lot more than if you need a few messages a second sent to a handful of recipients."
* "lower-volume network with a few dozen subscribers and a limited number of topics, we can use TCP and then
  the [XSUB and XPUB](https://zguide.zeromq.org/docs/chapter5/`Last`-Value-Caching)"
* "Let's imagine [our feed has an average of 100,000 100-byte messages a
  second](https://zguide.zeromq.org/docs/chapter5/`High`-Speed-Subscribers-Black-Box-Pattern) [...].
  While 100K messages a second is easy for a ZeroMQ application, ..."

**But we have:**

* few dozen subscribers             --> Check!
* limited number of topics          --> Check!
* max ~10 messages per second       --> Check!
* small common state information    --> Check!
* only the server updates the state --> Check!

This means, we can use less complex patters than used for these high-speed, high code count, high data rate networks :-)

* XPUB / XSUB to detect new subscriber
* Cache the entire state in the publisher
* Re-send the entire state on-demand (and then even to every subscriber)
* Using the same channel: sends state to every subscriber

**Reliability considerations**

* Late joining client (or drop-off and re-join): get full state update
* Server crash etc: No special handling necessary, we are simple
  and don't need recovery in this case. Server will publish initial state
  after re-start
* Subscriber too slow: Subscribers problem (TODO: Do we need to do anything about it?)

**Start-up sequence:**

* Publisher plugin is first plugin to be loaded
* Due to Publisher - PublisherServer structure no further sequencing required

### Plugin interactions and usage

RPC can trigger through function call in components/publishing plugin that

* entire state is re-published  (from the cache)
* a specific topic tree is re-published (from the cache)

Plugins publishing state information should publish initial state at @plugin.finalize

> [!IMPORTANT]
> Do not direclty instantiate the Publisher in your plugin module. Only one Publisher is
> required per thread. But the publisher instance **must** be thread-local!
> Always go through :func:`publishing.get_publisher()`.

**Sockets**

Three sockets are opened:

1. TCP (on a configurable port)
2. Websocket (on a configurable port)
3. Inproc: On ``inproc://PublisherToProxy`` all topics are published app-internally. This can be used for plugin modules
   that want to know about the current state on event based updates.

**Further ZeroMQ References:**

* [Working with Messages](https://zguide.zeromq.org/docs/chapter2/`Working`-with-Messages)
* [Multiple Threads](https://zguide.zeromq.org/docs/chapter2/`Multithreading`-with-ZeroMQ)


<a id="jukebox.publishing.server.PublishServer"></a>

## PublishServer Objects

```python
class PublishServer(threading.Thread)
```

The publish proxy server that collects and caches messages from all internal publishers and

forwards them to the outside world

Handles new subscriptions by sending out the entire cached state to **all** subscribers

The code is structures using a [Reactor Pattern](https://zguide.zeromq.org/docs/chapter5/`Using`-a-Reactor)


<a id="jukebox.publishing.server.PublishServer.run"></a>

#### run

```python
def run()
```

Thread's activity


<a id="jukebox.publishing.server.PublishServer.handle_message"></a>

#### handle\_message

```python
def handle_message(msg)
```

Handle incoming messages


<a id="jukebox.publishing.server.PublishServer.handle_subscription"></a>

#### handle\_subscription

```python
def handle_subscription(msg)
```

Handle new subscribers


<a id="jukebox.publishing.server.Publisher"></a>

## Publisher Objects

```python
class Publisher()
```

The publisher that provides the functional interface to the application

> [!NOTE]
> * An instance must not be shared across threads!
> * One instance per thread is enough


<a id="jukebox.publishing.server.Publisher.__init__"></a>

#### \_\_init\_\_

```python
def __init__(check_thread_owner=True)
```

**Arguments**:

- `check_thread_owner`: Check if send() is always called from the correct thread. This is debug feature
and is intended to expose the situation before it leads to real trouble. Leave it on!

<a id="jukebox.publishing.server.Publisher.send"></a>

#### send

```python
def send(topic: str, payload)
```

Send out a message for topic


<a id="jukebox.publishing.server.Publisher.revoke"></a>

#### revoke

```python
def revoke(topic: str)
```

Revoke a single topic element (not a topic tree!)


<a id="jukebox.publishing.server.Publisher.resend"></a>

#### resend

```python
def resend(topic: Optional[str] = None)
```

Instructs the PublishServer to resend current status to all subscribers

Not necessary to call after incremental updates or new subscriptions - that will happen automatically!


<a id="jukebox.publishing.server.Publisher.close_server"></a>

#### close\_server

```python
def close_server()
```

Instructs the PublishServer to close itself down


<a id="jukebox.daemon"></a>

# jukebox.daemon

<a id="jukebox.daemon.log_active_threads"></a>

#### log\_active\_threads

```python
@atexit.register
def log_active_threads()
```

This functions is registered with atexit very early, meaning it will be run very late. It is the best guess to

evaluate which Threads are still running (and probably shouldn't be)

This function is registered before all the plugins and their dependencies are loaded


<a id="jukebox.daemon.JukeBox"></a>

## JukeBox Objects

```python
class JukeBox()
```

<a id="jukebox.daemon.JukeBox.signal_handler"></a>

#### signal\_handler

```python
def signal_handler(esignal, frame)
```

Signal handler for orderly shutdown

On first Ctrl-C (or SIGTERM) orderly shutdown procedure is embarked upon. It gets allocated a time-out!
On third Ctrl-C (or SIGTERM), this is interrupted and there will be a hard exit!


<a id="jukebox.rpc.client"></a>

# jukebox.rpc.client

<a id="jukebox.rpc"></a>

# jukebox.rpc

<a id="jukebox.rpc.server"></a>

# jukebox.rpc.server

## Remote Procedure Call Server (RPC)

Bind to tcp and/or websocket port and translates incoming requests to procedure calls.
Avaiable procedures to call are all functions registered with the plugin package.

The protocol is loosely based on [jsonrpc](https://www.jsonrpc.org/specification)

But with different elements directly relating to the plugin concept and Python function argument options

    {
      'package'  : str  # The plugin package loaded from python module
      'plugin'   : str  # The plugin object to be accessed from the package
                        # (i.e. function or class instance)
      'method'   : str  # (optional) The method of the class instance
      'args'     : [ ]  # (optional) Positional arguments as list
      'kwargs'   : { }  # (optional) Keyword arguments as dictionary
      'as_thread': bool # (optional) start call in separate thread
      'id'       : Any  # (optional) Round-trip id for response (may not be None)
      'tsp'      : Any  # (optional) measure and return total processing time for
                        # the call request (may not be None)
    }

**Response**

A response will ALWAYS be send, independent of presence of 'id'. This is in difference to the
jsonrpc specification. But this is a ZeroMQB REQ/REP pattern requirement!

If 'id' is omitted, the response will be 'None'! Unless an error occurred, then the error is returned.
The absence of 'id' indicates that the requester is not interested in the response.
If present, 'id' and 'tsp' may not be None. If they are None, there are treated as if non-existing.

**Sockets**

Three sockets are opened

1. TCP (on a configurable port)
2. Websocket (on a configurable port)
3. Inproc: On ``inproc://JukeBoxRpcServer`` connection from the internal app are accepted. This is indented be
   call arbitrary RPC functions from plugins that provide an interface to the outside world (e.g. GPIO). By also going though
   the RPC instead of calling function directly we increase thread-safety and provide easy configurability (e.g. which
   button triggers what action)


<a id="jukebox.rpc.server.RpcServer"></a>

## RpcServer Objects

```python
class RpcServer()
```

The RPC Server Class


<a id="jukebox.rpc.server.RpcServer.__init__"></a>

#### \_\_init\_\_

```python
def __init__(context=None)
```

Initialize the connections and bind to the ports


<a id="jukebox.rpc.server.RpcServer.run"></a>

#### run

```python
def run()
```

The main endless loop waiting for requests and forwarding the

call request to the plugin module


<a id="misc"></a>

# misc

<a id="misc.recursive_chmod"></a>

#### recursive\_chmod

```python
def recursive_chmod(path, mode_files, mode_dirs)
```

Recursively change folder and file permissions

mode_files/mode dirs can be given in octal notation e.g. 0o777
flags from the stats module.

Reference: https://docs.python.org/3/library/os.html#os.chmod


<a id="misc.flatten"></a>

#### flatten

```python
def flatten(iterable)
```

Flatten all levels of hierarchy in nested iterables


<a id="misc.getattr_hierarchical"></a>

#### getattr\_hierarchical

```python
def getattr_hierarchical(obj: Any, name: str) -> Any
```

Like the builtin getattr, but descends though the hierarchy levels


<a id="misc.simplecolors"></a>

# misc.simplecolors

Zero 3rd-party dependency module to add colors to unix terminal output

Yes, there are modules out there to do the same and they have more features.
However, this is low-complexity and has zero dependencies


<a id="misc.simplecolors.Colors"></a>

## Colors Objects

```python
class Colors()
```

Container class for all the colors as constants


<a id="misc.simplecolors.resolve"></a>

#### resolve

```python
def resolve(color_name: str)
```

Resolve a color name into the respective color constant

**Arguments**:

- `color_name`: Name of the color

**Returns**:

color constant

<a id="misc.simplecolors.print"></a>

#### print

```python
def print(color: Colors,
          *values,
          sep=' ',
          end='\n',
          file=sys.stdout,
          flush=False)
```

Drop-in replacement for print with color choice and auto color reset for convenience

Use just as a regular print function, but with first parameter as color


<a id="misc.inputminus"></a>

# misc.inputminus

Zero 3rd-party dependency module for user prompting

Yes, there are modules out there to do the same and they have more features.
However, this is low-complexity and has zero dependencies


<a id="misc.inputminus.input_int"></a>

#### input\_int

```python
def input_int(prompt,
              blank=None,
              min=None,
              max=None,
              prompt_color=None,
              prompt_hint=False) -> int
```

Request an integer input from user

**Arguments**:

- `prompt`: The prompt to display
- `blank`: Value to return when user just hits enter. Leave at None, if blank is invalid
- `min`: Minimum valid integer value (None disables this check)
- `max`: Maximum valid integer value (None disables this check)
- `prompt_color`: Color of the prompt. Color will be reset at end of prompt
- `prompt_hint`: Append a 'hint' with [min...max, default=xx] to end of prompt

**Returns**:

integer value read from user input

<a id="misc.inputminus.input_yesno"></a>

#### input\_yesno

```python
def input_yesno(prompt,
                blank=None,
                prompt_color=None,
                prompt_hint=False) -> bool
```

Request a yes / no choice from user

Accepts multiple input for true/false and is case insensitive

**Arguments**:

- `prompt`: The prompt to display
- `blank`: Value to return when user just hits enter. Leave at None, if blank is invalid
- `prompt_color`: Color of the prompt. Color will be reset at end of prompt
- `prompt_hint`: Append a 'hint' with [y/n] to end of prompt. Default choice will be capitalized

**Returns**:

boolean value read from user input

<a id="misc.loggingext"></a>

# misc.loggingext

## Logger

We use a hierarchical Logger structure based on pythons logging module. It can be finely configured with a yaml file.

The top-level logger is called 'jb' (to make it short). In any module you may simple create a child-logger at any hierarchy
level below 'jb'. It will inherit settings from it's parent logger unless otherwise configured in the yaml file.
Hierarchy separator is the '.'. If the logger already exits, getLogger will return a reference to the same, else it will be
created on the spot.

Example: How to get logger and log away at your heart's content:

    >>> import logging
    >>> logger = logging.getLogger('jb.awesome_module')
    >>> logger.info('Started general awesomeness aura')

Example: YAML snippet, setting WARNING as default level everywhere and DEBUG for jb.awesome_module:

    loggers:
      jb:
        level: WARNING
        handlers: [console, debug_file_handler, error_file_handler]
        propagate: no
      jb.awesome_module:
        level: DEBUG


> [!NOTE]
> The name (and hierarchy path) of the logger can be arbitrary and must not necessarily match the module name (still makes
> sense).
> There can be multiple loggers per module, e.g. for special classes, to further control the amount of log output


<a id="misc.loggingext.ColorFilter"></a>

## ColorFilter Objects

```python
class ColorFilter(logging.Filter)
```

This filter adds colors to the logger

It adds all colors from simplecolors by using the color name as new keyword,
i.e. use %(colorname)c or {colorname} in the formatter string

It also adds the keyword {levelnameColored} which is an auto-colored drop-in replacement
for the levelname depending on severity.

Don't forget to {reset} the color settings at the end of the string.


<a id="misc.loggingext.ColorFilter.__init__"></a>

#### \_\_init\_\_

```python
def __init__(enable=True, color_levelname=True)
```

**Arguments**:

- `enable`: Enable the coloring
- `color_levelname`: Enable auto-coloring when using the levelname keyword

<a id="misc.loggingext.PubStream"></a>

## PubStream Objects

```python
class PubStream()
```

Stream handler wrapper around the publisher for logging.StreamHandler

Allows logging to send all log information (based on logging configuration)
to the Publisher.

> [!CAUTION]
> This can lead to recursions!
> Recursions come up when
> * Publish.send / PublishServer.send also emits logs, which cause a another send, which emits a log,
> which causes a send, .....
> * Publisher initialization emits logs, which need a Publisher instance to send logs

> [!IMPORTANT]
> To avoid endless recursions: The creation of a Publisher MUST NOT generate any log messages! Nor any of the
> functions in the send-function stack!


<a id="misc.loggingext.PubStreamHandler"></a>

## PubStreamHandler Objects

```python
class PubStreamHandler(logging.StreamHandler)
```

Wrapper for logging.StreamHandler with stream = PubStream

This serves one purpose: In logger.yaml custom handlers
can be configured (which are automatically instantiated).
Using this Handler, we can output to PubStream whithout
support code to instantiate PubStream keeping this file generic


