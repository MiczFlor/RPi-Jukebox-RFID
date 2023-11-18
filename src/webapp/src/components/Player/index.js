import React, { useContext, useEffect, useState } from 'react';

import Grid from '@mui/material/Grid';

import Cover from './cover';
import Controls from './controls';
import Display from './display';
import SeekBar from './seekbar';
import Volume from './volume';

import PlayerContext from '../../context/player/context';
import PubSubContext from '../../context/pubsub/context';
import request from '../../utils/request';
import { pluginIsLoaded } from '../../utils/utils';

const Player = () => {
  const { state: { playerstatus } } = useContext(PlayerContext);
  const { state: { 'core.plugins.loaded': plugins } } = useContext(PubSubContext);
  const { file } = playerstatus || {};

  const [coverImage, setCoverImage] = useState(undefined);
  const [backgroundImage, setBackgroundImage] = useState('none');

  useEffect(() => {
    const getMusicCover = async () => {
      const { result } = await request('musicCoverByFilenameAsBase64', { audio_src: file });
      if (result) {
        setCoverImage(result);
        setBackgroundImage([
          'linear-gradient(to bottom, rgba(18, 18, 18, 0.7), rgba(18, 18, 18, 1))',
          `url(data:image/jpeg;base64,${result})`
        ].join(','));
      };
    }

    if (pluginIsLoaded(plugins, 'music_cover_art') && file) {
      getMusicCover();
    }
  }, [file, plugins]);

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
