import React, { useContext } from 'react';

import PlayerContext from '../../context/player/context';

import makeStyles from '@mui/styles/makeStyles';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';

const useStyles = makeStyles({
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
    <Grid
      container
      sx={{
        marginBottom: '15px',
        marginTop: '15px',
      }}
    >
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
