import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';

import Cover from './cover';
import Controls from './controls';
import Display from './display';
import SeekBar from './seekbar';
import Volume from './volume';

const useStyles = makeStyles((theme) => ({
  root: {
    paddingTop: 20,
    paddingLeft: 20,
    paddingRight: 20,
  },
}));

const Player = () => {
  const classes = useStyles();

  return (
    <Grid container id="player" className={classes.root}>
      <Grid item xs={12} sm={5}>
        <Cover />
      </Grid>
      <Grid item xs={12} sm={7}>
        <Display />
        <SeekBar />
        <Controls />
        <Volume />
      </Grid>
    </Grid>
  );
};

export default Player;
