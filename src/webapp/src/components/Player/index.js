import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';

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
      <Grid container direction="row" justify="center" alignItems="center">
        <Grid item xs={6}>
          <Paper className={classes.paper}>
            <Display />
            <Controls />
          </Paper>
        </Grid>
      </Grid>
    </div>
  );
};

export default Player;
