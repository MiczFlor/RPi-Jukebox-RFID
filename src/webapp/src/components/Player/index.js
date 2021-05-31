import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';

import Cover from './cover';
import Controls from './controls';
import Display from './display';
import SeekBar from './seekbar';
import Volume from './volume';

const useStyles = makeStyles((theme) => ({
  paper: {
    marginTop: '20px',
    padding: '20px',
  },
}));

const Player = () => {
  const classes = useStyles();

  return (
    <div id="player">
      <Paper className={classes.paper}>
        <Cover />
        <Display />
        <SeekBar />
        <Controls />
        <Volume />
      </Paper>
    </div>
  );
};

export default Player;
