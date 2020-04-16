echo 'Install all required python modules'
pip install -r requirements.txt

echo 'Installing GPIO_Control service'
echo

FILE=$HOME/.config/phoniebox/gpio_settings.ini
if test -f "$FILE"; then
    echo "$FILE exist"
    echo "Script will not install a configuration"
else
    unset options i
    while IFS= read -r -d $'\0' f; do
      options[i++]="$f"
    done < <(find ./example_configs/ -maxdepth 1 -type f -name "*.ini" -print0 )


    echo  'Please choose a default configuration'
    select opt in "${options[@]}" "Stop the script"; do
      case $opt in
        *.ini)
          echo "Configuration  file $opt selected"
          echo "Copy file to $FILE"
          echo cp -v $opt $FILE
          cp -v $opt $FILE
          break
          ;;
        "Stop the script")
          echo "You chose to stop"
          break
          ;;
        *)
          echo "This is not a number"
          ;;
      esac
    done

fi
echo
echo 'Installing GPIO_Control service, this will require to enter your password up to 3 times to enable the service'
read -p "Press enter to continue " -n 1 -r
SERVICE_FILE=/etc/systemd/system/phoniebox_gpio_control.service
if test -f "$SERVICE_FILE"; then
   echo "$SERVICE_FILE exists.";
   read -p "Press enter to continue " -n 1 -r;
    #echo "systemctl daemon-reload"
    #systemctl daemon-reload
else
    sudo cp -v ./example_configs/phoniebox_gpio_control.service /etc/systemd/system/
    echo "systemctl start phoniebox_gpio_control.service"
    systemctl start phoniebox_gpio_control.service
    echo "systemctl enable phoniebox_gpio_control.service"
    systemctl enable phoniebox_gpio_control.service
fi
systemctl status phoniebox_gpio_control.service




