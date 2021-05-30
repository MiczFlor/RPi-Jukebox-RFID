import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import MusicNoteIcon from '@material-ui/icons/MusicNote';

const useStyles = makeStyles((theme) => ({
  cover: {
    width: '250px',
    height: '250px',
    display: 'flex',
  },
}));

const Cover = () => {
  const classes = useStyles();

  return (
    <Grid container direction="row" justify="center" alignItems="center">
      <Paper className={classes.cover} elevation={3}>
        <Grid container direction="row" justify="center" alignItems="center">
          <MusicNoteIcon  style={{ fontSize: 75 }} />
        </Grid>
      </Paper>
    </Grid>
  );
};

export default Cover;

