import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';

import Cover from './cover';
import Display from './display';
import Controls from './controls';

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
        <Controls />
      </Paper>
    </div>
  );
};

export default Player;
