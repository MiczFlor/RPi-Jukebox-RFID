import React from 'react';
import { Link } from 'react-router-dom';

import ArrowBackIcon from '@material-ui/icons/ArrowBack';
import IconButton from '@material-ui/core/IconButton';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
  header: {
    display: 'flex',
    alignItems: 'center',
  },
  withoutBackButton: {
    marginTop: 10,
    marginLeft: 20,
  }
}));


const Header = ({ title, backLink }) => {
  const classes = useStyles();

  return (
    <Grid container spacing={1} className={classes.header}>
      {backLink &&
        <IconButton
          aria-label="back"
          component={Link}
          to={backLink}
        >
          <ArrowBackIcon />
        </IconButton>
      }
      <Typography
        className={!backLink ? classes.withoutBackButton : null}
        variant="h6"
      >
        {title}
      </Typography>
    </Grid>
  );
};

export default Header;
