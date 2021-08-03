import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import MusicNoteIcon from '@material-ui/icons/MusicNote';

const useStyles = makeStyles((theme) => ({
  coverWrapper: {
    width: '70%',
    position: 'relative',
    paddingBottom: '70%',
  },
  cover: {
    position: 'absolute',
    width: '100%',
    height: '100%',
  }
}));

const Cover = () => {
  const classes = useStyles();

  return (
    <Grid container direction="row" justify="center" alignItems="center">
      <Paper className={classes.coverWrapper} elevation={3}>
        <Grid container direction="row" justify="center" alignItems="center" className={classes.cover}>
          <MusicNoteIcon  style={{ fontSize: 75 }} />
        </Grid>
      </Paper>
    </Grid>
  );
};

export default Cover;

