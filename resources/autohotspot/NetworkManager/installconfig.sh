#!/bin/bash
ver="0.8-1: 13 Dec 2023"
#Copyright Graeme Richards - RaspberryConnect.com
#Released under the GPL3 Licence (https://www.gnu.org/licenses/gpl-3.0.en.html)

#Installation and configuration script for AccessPopup script, that switches between
#a Wifi AccessPoint or connects to a Wifi Network as required

osver=($(cat /etc/issue))
cpath="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )/"

wdev0="wlan0"

script_path="/usr/bin/"
scriptname="accesspopup"
active_ap="n"
active=""
nw_profile=()

#service
sysd_path="/etc/systemd/system/"
service=AccessPopup.service
timer=AccessPopup.timer

#Text Format
YEL='\e[38;2;255;255;0m'
GRE='\e[38;0;255;0;0m'
DEF='\e[m'
BOL='\e[1m'


if [ "${osver[0]}" != 'Raspbian' ] && [ "${osver[0]}" != 'Debian' ]; then
	echo $YEL"This installer has only been tested on the Raspberry Pi's PiOS & Raspbian."$DEF
	echo "It may not work on other Debian based systems."
	echo "continue at your own risk"
fi
if [ "${osver[2]}" -ge 11 ]; then #OS Bullseye or later
	echo 'OS Version' "${osver[2]}"
elif [ "${osver[2]}" -lt 11 ];then #older OS
	echo "The version of PiOS or Raspbian is too old for the $scriptname script"
	echo "Version 11 'Bullseye' with Network Manager enabled in raspi-config is the minimum requirement"
	echo "A version for your OS is available at RaspberryConnect.com using dhcpcd instead."
	echo "www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/183-raspberry-pi-automatic-hotspot-and-static-hotspot-installer"
	exit 1
fi

if nmcli -t -f RUNNING general | grep -v "running" ;then #NM not running
	echo "Network Manager is required but is not the active system network service"
	echo "Unable to continue."
	exit 1
fi

add_service()
{
if systemctl -all list-unit-files $service | grep -v $service ;then
cat > "$sysd_path$service" <<EOF
[Unit]
Description=Automatically generates an Access Point when a valid SSID is not in range
After=multi-user.target
Requires=network-online.target
[Service]
Type=simple
ExecStart=$script_path$scriptname
[Install]
WantedBy=multi-user.target
EOF
systemctl unmask $service
fi
}

add_timer_service()
{
if systemctl -all list-unit-files $timer | grep -v $timer ;then
cat > "$sysd_path$timer" <<EOF
[Unit]
Description=$scriptname network checks every 2 mins

[Timer]
OnBootSec=0min
OnCalendar=*:0/2

[Install]
WantedBy=timers.target
EOF
systemctl unmask $timer
systemctl enable $timer
systemctl daemon-reload
fi
}


#Function what is the current active wifi
active_wifi()
{
	act="$(nmcli -t -f TYPE,NAME,DEVICE,TYPE con show --active | grep "$wdev0")" #List of active devices
	act="$(awk 1 ORS=':' <(echo "$act"))" #Replaces LF with : Delimeter
	readarray -d ':' -t active_name < <(printf "%s" "$act") #Change to array output
	if [ ! -z active ]; then
		active="${active_name[1]}"
		#echo "active_wifi: added $active"
	else
		active=""
	fi
}

#Function is the current Connection an AP
is_active_ap()
{
active_ap="n"
if [ ! -z "$active" ] ; then
	mode="$(nmcli con show "$active" | grep 'wireless.mode')"
	readarray -d ':' -t mode < <(printf "%s" "$mode")
	if [ ! -z mode ]; then
		mode2="$(echo "${mode[1]}" | sed 's/[[:blank:]]//g')"
		if [ "$mode2" = "ap" ]; then
			active_ap="y"
		fi
	fi
fi
}

switch()
{
	active_wifi
	is_active_ap
	echo "active_ap status is:" $active_ap
	if [ "$active_ap" = "y" ]; then #Yes active profile is an AP
		echo "Attempting to switch to WiFi Network"
		"$script_path$scriptname"
	else
		echo "Switching to AP"
		"$script_path$scriptname" "-a"
	fi	
}

install()
{
	if [ -f "./$scriptname" ]; then
		cp "./$scriptname" "$script_path"
		chmod +x "$script_path$scriptname"
		add_service
		add_timer_service
		systemctl start $timer
		$script_path$scriptname
	else
		echo "$scriptname is not in the same location as this installer"
		echo "Unable to continue"
	fi
}

ap_ssid_change()
{
	if [ -f "$script_path$scriptname" ] >/dev/null 2>&1; then 
		echo -e "The current ssid and password for the AP are:"
		ss="$( grep -F 'ap_ssid=' $script_path$scriptname )"
		echo "SSID:${ss:8}"
		pw="$( grep -F 'ap_pw=' $script_path$scriptname )"
		echo "Password:${pw:6}"
		prof="$( grep -F 'ap_profile_name=' $script_path$scriptname )"
		echo -e $YEL"Enter the new SSID"$DEF
		echo "Press enter to keep the existing SSID"
		read newss
		if [ ! -z "$newss" ]; then
			sed -i "s/ap_ssid=.*/ap_ssid='$newss'/" "$script_path$scriptname"
		fi
		echo -e $YEL"Enter the new Password"$DEF
		echo "The password must be at least 8 characters"
		echo "Press enter to keep the existing Pasword"
		read newpw
		if [ ! -z "Snewpw" ] && [ ${#newpw} -ge 8 ]; then
			sed -i "s/ap_pw=.*/ap_pw='$newpw'/" "$script_path$scriptname"
		fi
		echo "The Access Points SSID and Password are:"
		ss="$( grep -F 'ap_ssid=' $script_path$scriptname )"
		pw="$( grep -F 'ap_pw=' $script_path$scriptname )"
		echo "SSID:${ss:8}"
		echo "Password: ${pw:6}"
		#remove AP profile
		pro="$(nmcli -t -f NAME con show | grep ${prof:17:-1} )"
		if [ ! -z "$pro" ]; then
			nmcli con delete "$pro" >/dev/null 2>&1
			nmcli con reload
		fi
	else
		echo "$scriptname is not available."
		echo "Please install the script first"
	fi
}

ap_change_ip()
{
	#IP network address
	if [ -f "$script_path$scriptname" ] >/dev/null 2>&1; then 
		echo "The current AP IP address is:"
		ip="$( grep -F 'ap_ip=' $script_path$scriptname )"
		echo -e $YEL"${ip:7:-1}"$DEF
		r="0"
		until [[ "$r" -eq 3 ]]; do
			echo -e "\nChoose IP Network. The first two parts of the IP address"
			echo "1) 192.168."
			echo "2) 10.0."
			echo "3) Exit"
			read r
			if [ ! -z "$r" ]; then
				case $r in
					1) 
						ipnw="192.168."
						r=3
						;;
					2)
						ipnw="10.0."
						r=3
						;;
					3)
						ipnw="0" ; clear; menu ;;
					*)
						echo -e $BOL$YEL"\nInvalid option"$DEF
						;;
					esac
				fi
			done
		#IP host 1 values
		if [[ ! $ipnw = "0" ]]; then
			r2=0
			until [ "$r2" -eq 1 ]; do
				echo -e "\n${BOL}Enter the first host number $ipnw###${DEF}"
				echo "Valid numbers between 0 and 255"
				echo -e "The number must not match the third position of other networks connected to your"
				echo "device starting with $ipnw such as an ethernet ip or second wifi network"
				echo "Enter 999 to exit"
				read iph1
				if [[ $iph1 =~ ^[0-9]+$ ]]; then
					if [ $iph1 = 999 ]; then
						iph1=""
						r2=1
					elif [ $iph1 -lt 0 ] || [ $iph1 -gt 255 ]; then
						echo -e ${BOL}"\nNot a valid number\n"${DEF}
						r2=0
					else
						#Valid entry, next menu
						r2=1
					fi
				else
					r2=0
				fi
			done
		fi
		#IP host 2 values
		if [ ! -z $ipnw ] && [ ! -z $iph1 ]; then 
			r3=0
			until [ "$r3" -eq 1 ]; do
				echo -e ${BOL}"\nEnter the second host number $ipnw$iph1.###"${DEF}
				echo "Valid numbers between 0 and 253"
				echo "Enter 999 to exit"
				read iph2
				if [[ $iph2 =~ ^[0-9]+$ ]]; then
					if [ $iph2 -eq 999 ]; then
						iph2=""
						r3=1
					elif [ $iph2 -lt 0 ] || [ $iph2 -gt 253 ]; then
						echo -e ${BOL}"\nNot a valid number\n"${DEF}
						r3=0
					else
						#Valid entry, next menu
						r3=1
					fi
				else
					r3=0
				fi
			done
		fi
		if [ ! -z "$r3" ];then
			echo -e ${BOL}"\nUpdating the Access Point to IP address to:"${DEF}
			ipa="$ipnw$iph1.$iph2"
			ipg="$ipnw$iph1.254"
			echo -e ${YEL}$ipa${DEF}
			sed -i "s/ap_ip=.*/ap_ip='$ipa\\/24'/" "$script_path$scriptname"
			sed -i "s/ap_gate=.*/ap_gate='$ipg'/" "$script_path$scriptname"
			
			prof="$( grep -F 'ap_profile_name=' $script_path$scriptname )"
			pro="$(nmcli -t -f NAME con show | grep ${prof:17:-1} )"
			if [ ! -z "$pro" ]; then
				nmcli con delete "$pro" >/dev/null 2>&1
			fi
			echo -e "\ncomplete"
		fi
	else
		echo "$scriptname is not available."
		echo "Please install the script first"
	fi
}

saved_profiles()
{
ap_profile=()
nw_profile=()
n="$(nmcli -t -f TYPE,NAME,ACTIVE con show)" #Capture Output
n="$(awk 1 ORS=':' <(echo "$n"))" #Replaces LF with : Delimeter
readarray -d ':' -t profiles < <(printf "%s" "$n") #Change to array output
if [ ! -z profiles ]; then
	for (( c=0; c<=${#profiles[@]}; c+=3 )) #array of profiles
	do
		if [ ! -z "${profiles[$c+1]}" ] ; then
			mode="$(nmcli con show "${profiles[$c+1]}" | grep 'wireless.mode')" #show mode infurstructure, AP
			readarray -d ':' -t mode < <(printf "%s" "$mode")
			mode2="$(echo "${mode[1]}" | sed 's/[[:blank:]]//g')"
			if [ "$mode2" = "infrastructure" ]; then
				nw_profile+=("${profiles[$c+1]}")
			fi
		fi
	done
fi
}


setupssid()
{
	echo -e $YEL$BOL"Add or Edit a Wifi Network"$DEF
	echo "Add a new WiFi network or change the password for an existing one that is in range"
	ct=0; j=0 ; lp=0
	wfselect=()

	until [ $lp -eq 1 ] #wait for wifi if busy, usb wifi is slower.
	do
		IFS=$'\n:$\t' localwifi=($((iw dev wlan0 scan ap-force | egrep "SSID:") 2>&1)) >/dev/null 2>&1
		#if wifi device errors recheck
		if (($j >= 5)); then #if busy 5 times exit to menu
			echo "WiFi Device Unavailable, cannot scan for wifi devices at this time"
			echo "press a key to continue"
			j=99
			read
			#break
		elif echo "${localwifi[1]}" | grep "No such device (-19)" >/dev/null 2>&1; then
			echo "No Device found,trying again"
			j=$((j + 1))
			sleep 2
		elif echo "${localwifi[1]}" | grep "Network is down (-100)" >/dev/null 2>&1 ; then
			echo "Network Not available, trying again"
			j=$((j + 1))
			sleep 2
		elif echo "${localwifi[1]}" | grep "Read-only file system (-30)" >/dev/null 2>&1 ; then
			echo "Temporary Read only file system, trying again"
			j=$((j + 1))
			sleep 2
		elif echo "${localwifi[1]}" | grep "Invalid exchange (-52)" >/dev/null 2>&1 ; then
			echo "Temporary unavailable, trying again"
			j=$((j + 1))
			sleep 2
		elif echo "${localwifi[1]}" | grep -v "Device or resource busy (-16)"  >/dev/null 2>&1 ; then
			lp=1
		else #see if device not busy in 2 seconds
			echo "WiFi Device unavailable checking again"
			j=$((j + 1))
			sleep 2
		fi
	done
	if [ $j -eq 99 ]; then
		menu
	fi
	#Wifi Connections found - continue
	for x in "${localwifi[@]}"
	do
		if [ $x != "SSID" ]; then #list available local wifi networks
			if [ ! -z ${x/ /} ];then
				ct=$((ct + 1))
				echo "$ct  ${x/ /}"
				wfselect+=("${x/ /}")
			fi
		fi
	done
	ct=$((ct + 1)) 
	echo  "$ct To Cancel"
	wfselect+=("Cancel")
	if [ "${#wfselect[@]}" -eq 1 ] ;then
		echo "Unable to detect local WiFi Networks. Maybe there is a temporary issue with the WiFi"
		echo "Try again in a minute"
		echo "press enter to continue"
		read
		menu
	fi

	read wf
	if [[ $wf =~ ^[0-9]+$ ]]; then
		if [ $wf -ge 0 ] && [ $wf -le $ct ]; then
			updatessid "${wfselect[$wf-1]}"
		else
			echo -e $YEL"\nNot a Valid entry"$DEF
			setupssid
		fi
	else
		echo -e $YEL"\nNot a Valid entry"$DEF
		setupssid
	fi
}

updatessid()
{
	d=0
	echo "$1"
	echo ""
	if [ "$1" = "Cancel" ] || [ "$1" = "" ] ; then
		clear
		menu
	fi
	saved_profiles
	for x in "${nw_profile[@]}"
	do
		idssid=$(nmcli -t con show "$x" | grep "wireless.ssid")
		#echo "The SSID for profile is ${idssid:21}"
		if [ "${idssid:21}" = "$1" ]; then
			#edit password
			echo "Enter the new password for PROFILE: $x SSID: $1"
			echo "This must be at least 8 characters."
			read ssidpw
			if [ ! -z "$ssidpw" ] && [ ${#ssidpw} -ge 8 ] ;then
				nmcli con modify "$x" wifi-sec.psk "$ssidpw"
				echo -e "\nPassword for profile $x is"
				npw="$(nmcli -t -s con show "$x" | grep 'wireless-security.psk:' )"	
				echo ${npw:29}
				d=1	
				break
			else
				echo "A password was not entered or is less than 8 characters"
				echo "The password has not been changed"
				d=2
			fi
		fi
	done
	
	if [ $d -eq 0 ]; then #no existing profile for selection
		echo -e $YEL"Enter the Password for the Selected Wifi Network"$DEF
		echo "This must be at least 8 characters"
		echo "Selected SSID: $1"
		echo -e "\nEnter password for the Wifi Network"
		read chgpw
		echo "Attempting to connect to new Wifi Network"
		if [ ! -z "$chgpw" ] && [ "${#chgpw}" -ge 8 ] ;then
			#create new profile with details
			nmcli dev wifi con "$1" password "$chgpw"
			echo "Profile Created"
			echo "$1"
			pw="$( nmcli -t -s con show $1 | grep 'wireless-security.psk:' )"
			echo ${pw:29}
		else
			echo "A password was not entered or is less than 8 characters"
			echo "The password has not ben changed"
		fi
	fi
}

# if password is bad then after 30 seconds or so
#Error: Connection activation failed: Secrets were required, but not provided.


#Function Change Hostname
namehost()
{
		hn="$(nmcli general hostname)"
		echo -e $YEL"System Hostname is: $hn"$DEF
		echo "Enter a new hostname or"
		echo "just press enter to keep existing hostname"
		read r
		if [ ! -z $r ]; then
			nmcli general hostname "$r"
			echo "The hostname has been changed"
		fi
		hn="$(nmcli general hostname)"
		echo "Current Hostname is: $hn"
}
uninstall()
{
	echo "Uninstalling $scriptname"
	if systemctl -all list-unit-files $service | grep $service ;then
		systemctl unmask $service
		systemctl disable $service
		rm /etc/systemd/system/$service
	fi
	if systemctl -all list-unit-files $timer | grep $timer ;then
		systemctl unmask $timer
		systemctl disable $timer
		rm /etc/systemd/system/$timer
		systemctl daemon-reload
	fi		
	if [ -f "$script_path$scriptname" ]; then
		profap="$( grep -F ap_profile_name= $script_path$scriptname )"
		nmcli con delete "${profap:17:-1}"
		nmcli con reload
		rm  "$script_path$scriptname"
	fi
	echo "Uninstall complete"
}

go()
{
	opt="$1"
	if [ "$opt" = "INS" ] ;then
		if ls "$script_path" | grep "$scriptname" >/dev/null 2>&1; then
			echo "$scriptname is already installed"
		else
			echo "Installing Script"
			install
		fi			
	elif [ "$opt" = "SSI" ] ;then
		#"Change the Access Points SSID and Password"
		ap_ssid_change
	elif [ "$opt" = "NWK" ] ;then
		setupssid
	elif [ "$opt" = "SWI" ] ;then
		echo -e $YEL"Switching between WiFi Network and WiFi Access Point."$DEF
		if [ -f "$script_path$scriptname" ]; then
			switch
		else
			echo "$scriptname is not currently installed."
			echo "Please install it first"
		fi
	elif [ "$opt" = "IPA" ] ;then
		echo -e "${BOL}Set IP address for AP${DEF}"
		ap_change_ip
	elif [ "$opt" = "UNI" ] ;then
		if ls $script_path | grep $scriptname >/dev/null 2>&1 ; then
			uninstall
		else
			echo "$scriptname is not installed"
		fi
	elif [ "$opt" = "RUN" ] ;then
		if [ -f "$script_path$scriptname" ]; then
			echo "Running the Script now"
			 "$script_path$scriptname"
		else
			echo "$scriptname is not available."
			echo "Please install the script first"
		fi
	elif [ "$opt" = "HST" ] ;then
		namehost	
	fi
	echo "Press any key to continue"
	read
	clear
	menu
}

menu()
{
#selection menu
clear
until [ "$select" = "9" ]; do
	active_wifi
	curip="$(nmcli -t con show $active | grep IP4.ADDRESS)"
	readarray -d ':' -t ipid < <(printf "%s" "$curip")
	showip="$(echo "${ipid[1]}" | sed 's/[[:blank:]]//g')"
	
	echo -e $YEL"Raspberryconnect.com"
	echo "AccessPopup installation and setup"
	echo -e "Version $ver  Installs AccessPopup ver 0.8 12 Dec 2023"$DEF

	echo "Connects to your home network when you are home or a nearby know wifi network."
	echo "If no known wifi network is found then an Access Point is automatically activated"
	echo -e "until a known network is back in range\n"
	if [ -z "$active" ]; then
		echo "Not currently using a Wifi profile"
	else
		echo "Currently using WiFi profile: $active"
		if [ ! -z $showip ]; then
			echo "Current WiFi IP address is: ${showip::-3}"
		fi
		hn="$(nmcli general hostname)"
		echo "System Hostname is: $hn" 

	fi
	echo ""
	echo " 1 = Install AccessPopup Script"
	echo " 2 = Change the Access Points SSID or Password"
	echo " 3 = Change the Access Points IP Address"
	echo " 4 = Live Switch between: Network WiFi <> Access Point"
	echo " 5 = Setup a New WiFi Network or change the password to an existing Wifi Network"
	echo " 6 = Change Hostname"
	echo " 7 = Uninstall $scriptname"
	echo " 8 = Run $scriptname now. It will decide between a suitable WiFi network or AP."
	echo " 9 = Exit"
	echo ""
	echo "The Wifi status will be checked every 2 minutes. Switching will happen when a"
	echo "valid wifi network comes in and out of range."
	echo "use option 4 or the command: sudo $scriptname -a"
	echo "to activate a permanant access point, until the next reboot" 
	echo "or when just sudo $scriptname is used."
	echo -e -n "\nSelect an Option:"
	read select
	case $select in
	1) clear ; go "INS" ;; #Install AccessPopup 
	2) clear ; go "SSI" ;; #Set the AP SSID and Password
	3) clear ; go "IPA" ;; #Set the Access Points IP Address
	4) clear ; go "SWI" ;; #Live Switch: NW <> AP
	5) clear ; go "NWK" ;; #Connect to New WiFi Network
	6) clear ; go "HST" ;; #Change Hostname
	7) clear ; go "UNI" ;; #Uninstall AccessPopup
	8) clear ; go "RUN" ;; #Run the AccessPopup script now
	9) clear ; exit ;;
	*) clear; echo -e "Please select again\n";;
	esac
done
}
menu
