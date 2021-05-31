import React, { useContext } from 'react';

import SocketContext from '../../context/sockets/context';

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

  const { playerStatus: { status } } = useContext(SocketContext);

  return (
    <Box my={4}>
      <Typography className={classes.dontBreak} component="h5" variant="h5">
        {status?.songid ? status?.title : 'No song in queue' }
      </Typography>
      <Typography className={classes.dontBreak} variant="subtitle1" color="textSecondary">
        {status?.songid && status?.artist }
        <span className={classes.divider}>&bull;</span>
        {status?.songid && status?.album }
      </Typography>
    </Box>
  );
};

export default Display;
