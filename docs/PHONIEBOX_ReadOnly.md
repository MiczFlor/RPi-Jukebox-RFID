# Phoniebox with read-only Filesystem 

In order to make the Phoniebox more resilient against sudden power loss a mostly read-only filesystem helps against filesystem corruption.

First we need to mount a read-write Partition to /home/pi/RPi-Jukebox-RFID/shared/. This can bei either a further partition on the SD 
card or an USB drive connected to the Pi. If you want to store the shared partition on the sd card you need to first resize the main
partition. In a normal raspbian install there is one small partition and one that fills the rest of the card. There is a good HOWTO on how 
to resize the partition here: https://www.howtoforge.com/partitioning_with_gparted

Please resize the partition AFTER the first boot of teh systtem since Raspbian tries to resize the partition on the sd card to fill the 
whole card this process seems to fail if there is a partition in the way.

Before the new partition can be mounted the original shared directory with its contents needs to be moved out of the way:

```
cd ~/RPi-Jukebox-RFID/
mv shared shared.old
mkdir shared
```

Then we need to find out the PARTUUID of the newly created partition with the command blkid. It should produce the following output:

```
pi@JukeboxJan:~/RPi-Jukebox-RFID $ blkid
/dev/mmcblk0p1: LABEL="boot" UUID="9304-D9FD" TYPE="vfat" PARTUUID="9282f822-01"
/dev/mmcblk0p2: LABEL="rootfs" UUID="29075e46-f0d4-44e2-a9e7-55ac02d6e6cc" TYPE="ext4" PARTUUID="9282f822-02"
/dev/mmcblk0p3: LABEL="shared" UUID="821fcedf-b705-4515-a5e8-2e99beefc1bf" TYPE="ext4" PARTUUID="9282f822-03"
```

In order to mount the rw partition to ~/RPi-Jukebox-RFID/shared/ on bootup you need to add the following line to /etc/fstab Replace the PARTUUID with teh one from your output. (Don't forget you need to ```sudo vi /etc/fstab``` to edit the file)

```
PARTUUID="9282f822-03" /home/pi/RPi-Jukebox-RFID/shared ext4 defaults,noatime 0 2 
```

```sudo mount -a``` will mount the new partition to its mountpoint. 

Now adjust the ownership and permissions of the new shared directory:

```
sudo chown pi:www-data shared
sudo chmod 775 shared
```

Rsync the contents of shared.old into share:

````
rsync -av shared.old/* shared/
````

Some settings need to persist between boots, others are not necessarily persistend. Those that need to be persistent are symlinked to 
a new directory shared/settings, the others are symlinked to files in /var/tmp that will reside on a ramdisk.

```
ln -sf /var/tmp/Latest_RFID ~/RPi-Jukebox-RFID/settings
ln -sf /var/tmp/Latest_Folder_Played ~/RPi-Jukebox-RFID/settings
ln -sf /var/tmp/Latest_Playlist_Played ~/RPi-Jukebox-RFID/settings
ln -sf /var/tmp/latestID.txt ~/RPi-Jukebox-RFID/shared/

mkdir ~/RPi-Jukebox-RFID/shared/settings
mv Audio_Folders_Path Audio_Volume_Change_Step  Idle_Time_Before_Shutdown Max_Volume_Limit Playlists_Folders_Path Second_Swipe ShowCover ../shared/settings/
ln -sf ~/RPi-Jukebox-RFID/shared/settings/* ~/RPi-Jukebox-RFID/settings/
```


Add the following lines to the fstab:

```sudo vi /etc/fstab```

```
tmpfs           /var/log        tmpfs   nodev,nosuid          0 0
tmpfs           /var/lib/samba  tmpfs   nodev,nosuid          0 0
tmpfs           /var/lib/mpd  tmpfs   nodev,nosuid          0 0
tmpfs           /var/cache/samba  tmpfs   nodev,nosuid          0 0
tmpfs           /var/tmp        tmpfs   nodev,nosuid          0 0
tmpfs           /tmp            tmpfs   nodev,nosuid          0 0
```

If you have not yet created a password for the Samba User pi, do it now, before moving the files away:

```sudo smbpasswd pi```

Move Samba files away and create mount point for a tmpfs:
```
sudo mv /var/lib/samba /var/lib/samba.save
sudo mkdir /var/lib/samba
```

```sudo vi /etc/tmpfiles.d/smb.conf```

paste 
```
#Type Path        Mode UID  GID  Age Argument
C     /var/lib/samba/private  - - - - /var/lib/samba.save/private
C	  /var/lib/samba/account_policy.tdb - - - - /var/lib/samba.save/account_policy.tdb
C	  /var/lib/samba/group_mapping.tdb - - - - /var/lib/samba.save/group_mapping.tdb
C	  /var/lib/samba/printers - - - - /var/lib/samba.save/printers
C	  /var/lib/samba/registry.tdb - - - - /var/lib/samba.save/registry.tdb
C	  /var/lib/samba/share_info.tdb - - - - /var/lib/samba.save/share_info.tdb
C	  /var/lib/samba/usershares - - - - /var/lib/samba.save/usershares
C	  /var/lib/samba/wins.dat - - - - /var/lib/samba.save/wins.dat
C	  /var/lib/samba/wins.tdb - - - - /var/lib/samba.save/wins.tdb
d     /var/log/samba  0750 root adm - -
```


```sudo vi /etc/tmpfiles.d/lighttpd.conf```

paste

```
#Type Path        Mode UID  GID  Age Argument
d     /var/log/lighttpd  0755 www-data www-data - -
```

Change settings/Playlist_Folders_Path to shared/playlists

Edit /etc/mpd.conf and change log_file from /var/log/mpd/mpd.log to /var/log/mpd.log

If you need to make changes to your root filesystem in the future you need to remount it in read-write mode. 

This can be done with the command ```mount -o remount,rw /``` and reversed by ```mount -oremount,to /```

Sources: 
* https://kofler.info/raspbian-lite-fuer-den-read-only-betrieb/ and
* https://petr.io/en/blog/2015/11/09/read-only-raspberry-pi-with-jessie/

