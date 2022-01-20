import React, { useContext, useEffect, useState } from 'react';

import Grid from '@mui/material/Grid';

import Cover from './cover';
import Controls from './controls';
import Display from './display';
import SeekBar from './seekbar';
import Volume from './volume';

import PubSubContext from '../../context/pubsub/context';

const Player = () => {
  const { state: { player_status } } = useContext(PubSubContext);

  const [coverImage, setCoverImage] = useState(undefined);
  const [backgroundImage, setBackgroundImage] = useState('none');

  useEffect(() => {
    if (player_status?.coverArt) {
      const coverImageSrc = `https://i.scdn.co/image/${player_status.coverArt}`;
      setCoverImage(coverImageSrc);
      setBackgroundImage([
        'linear-gradient(to bottom, rgba(18, 18, 18, 0.7), rgba(18, 18, 18, 1))',
        `url(${coverImageSrc})`
      ].join(','));
    }
  }, [player_status]);

  return (
    <Grid
      container
      id="player"
      sx={{
        backgroundImage,
        backgroundPosition: 'center',
      }}
    >
      <Grid
        container
        sx={{
          paddingTop: '30px',
          paddingLeft: '30px',
          paddingRight: '30px',
          minHeight: 'calc(100vh - 64px - 10px)',
          backdropFilter: 'blur(25px)',
        }}
      >
        <Grid item xs={12} sm={5}>
          <Cover coverImage={coverImage} />
        </Grid>
        <Grid item xs={12} sm={7}>
          <Display />
          <SeekBar />
          <Controls />
          <Volume />
        </Grid>
      </Grid>
    </Grid>
  );
};

export default Player;
