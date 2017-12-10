# USB audio card on Jessie

Check if the device is recognised:
```
$ cat /proc/asound/modules 
 0 snd_bcm2835
 1 snd_usb_audio
```
This shows that device 1 is the usb audio card.

Open the sound configuration file.
```
$ sudo nano /usr/share/alsa/alsa.conf
```
Now replace the lines near the end of the file:
```
defaults.ctl.card 0
defaults.pcm.card 0
```
with:
```
defaults.ctl.card 1
defaults.pcm.card 1
```
Now the audio card for the system is set to 1. Reboot the RPi:
```
$ sudo reboot
```