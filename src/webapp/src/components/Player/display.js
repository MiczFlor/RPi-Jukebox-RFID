import React, { useContext } from 'react';

import PlayerContext from '../../context/player/context';

import { makeStyles } from '@material-ui/core/styles';
import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';

const useStyles = makeStyles({
  bar: {
    transition: 'none',
  },
  divider: {
    marginLeft: '5px',
    marginRight: '5px',
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
    <Box my={4}>
      <Typography className={classes.dontBreak} component="h5" variant="h5">
        {playerstatus?.songid ? (playerstatus?.title || 'Unknown title' ) : 'No song in queue' }
      </Typography>
      <Typography className={classes.dontBreak} variant="subtitle1" color="textSecondary">
        {playerstatus?.songid && (playerstatus?.artist || 'Unknown artist') }
        <span className={classes.divider}>&bull;</span>
        {playerstatus?.songid && (playerstatus?.album || playerstatus?.file) }
      </Typography>
    </Box>
  );
};

export default Display;
