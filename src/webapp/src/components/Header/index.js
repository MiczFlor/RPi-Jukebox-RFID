import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import IconButton from '@mui/material/IconButton';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';

const Header = ({ title, backLink }) => {
  const { t } = useTranslation();

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
          aria-label={t('header.back')}
          component={Link}
          to={backLink}
          size="large"
          title={t('header.back')}
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
