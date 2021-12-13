import React from 'react';

import Battery20Icon from '@mui/icons-material/Battery20';
import Battery30Icon from '@mui/icons-material/Battery30';
import Battery50Icon from '@mui/icons-material/Battery50';
import Battery60Icon from '@mui/icons-material/Battery60';
import Battery80Icon from '@mui/icons-material/Battery80';
import Battery90Icon from '@mui/icons-material/Battery90';
import BatteryFullIcon from '@mui/icons-material/BatteryFull';
import BatteryCharging20Icon from '@mui/icons-material/BatteryCharging20';
import BatteryCharging30Icon from '@mui/icons-material/BatteryCharging30';
import BatteryCharging50Icon from '@mui/icons-material/BatteryCharging50';
import BatteryCharging60Icon from '@mui/icons-material/BatteryCharging60';
import BatteryCharging80Icon from '@mui/icons-material/BatteryCharging80';
import BatteryCharging90Icon from '@mui/icons-material/BatteryCharging90';
import BatteryChargingFullIcon from '@mui/icons-material/BatteryChargingFull';
import BatteryUnknownIcon from '@mui/icons-material/BatteryUnknown';

const BatteryIcon = ({ soc, charging }) => {
  if (charging) {
    if (soc <= 20) return <BatteryCharging20Icon />;
    else if (soc > 20 && soc <= 30) return <BatteryCharging30Icon />;
    else if (soc > 30 && soc <= 50) return <BatteryCharging50Icon />;
    else if (soc > 50 && soc <= 60) return <BatteryCharging60Icon />;
    else if (soc > 60 && soc <= 80) return <BatteryCharging80Icon />;
    else if (soc > 80 && soc <= 90) return <BatteryCharging90Icon />;
    else if (soc > 90) return <BatteryChargingFullIcon />;
  }
  else {
    if (soc <= 20) return <Battery20Icon />;
    else if (soc > 20 && soc <= 30) return <Battery30Icon />;
    else if (soc > 30 && soc <= 50) return <Battery50Icon />;
    else if (soc > 50 && soc <= 60) return <Battery60Icon />;
    else if (soc > 60 && soc <= 80) return <Battery80Icon />;
    else if (soc > 80 && soc <= 90) return <Battery90Icon />;
    else if (soc > 90) return <BatteryFullIcon />;
  }

  return <BatteryUnknownIcon />;
};

export default BatteryIcon;
