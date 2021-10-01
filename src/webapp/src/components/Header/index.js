import React from 'react';
import { Link } from 'react-router-dom';

import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import IconButton from '@mui/material/IconButton';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';

const Header = ({ title, backLink }) => {
  return (
    <Grid
      container
      spacing={1}
      sx={{
        display: 'flex',
        alignItems: 'center',
      }}
    >
      {backLink &&
        <IconButton
          aria-label="back"
          component={Link}
          to={backLink}
          size="large"
        >
          <ArrowBackIcon />
        </IconButton>
      }
      <Typography
        variant="h6"
        sx={
          !backLink
          ? {
              marginTop: '10px',
              marginLeft: '20px',
            }
          : {}
        }
      >
        {title}
      </Typography>
    </Grid>
  );
};

export default Header;
