import React from 'react';

import {
  Box,
  CircularProgress,
  Switch,
} from '@mui/material';

const SwitchWithLoader = ({
  isLoading,
  checked,
  disabled,
  onChange
}) => {
  return (
    <Box sx={{
      display: 'flex',
      alignItems: 'center',
      marginLeft: '0',
    }}>
      {isLoading && <CircularProgress size={20} />}
      <Switch
        checked={checked}
        disabled={isLoading || disabled}
        onChange={onChange}
      />
    </Box>
  );
};

export default SwitchWithLoader;
