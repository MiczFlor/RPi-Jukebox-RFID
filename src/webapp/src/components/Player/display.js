import React, { useContext } from 'react';

import PlayerContext from '../../context/player/context';

import { makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

const useStyles = makeStyles({
  wrapper: {
    marginBottom: 15,
    marginTop: 15,
  },
  divider: {
    marginLeft: 5,
    marginRight: 5,
  },
  dontBreak: {
    whiteSpace: 'nowrap',
    width: '100%',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  }
});

const Display = () => {
  const classes = useStyles();
  const { state: { playerstatus } } = useContext(PlayerContext);

  return (
    <Grid container className={classes.wrapper}>
      <Typography className={classes.dontBreak} component="h5" variant="h5">
        {playerstatus?.songid ? (playerstatus?.title || 'Unknown title' ) : 'No song in queue' }
      </Typography>
      <Typography className={classes.dontBreak} variant="subtitle1" color="textSecondary">
        {playerstatus?.songid && (playerstatus?.artist || 'Unknown artist') }
        <span className={classes.divider}>&bull;</span>
        {playerstatus?.songid && (playerstatus?.album || playerstatus?.file) }
      </Typography>
    </Grid>
  );
};

export default Display;
