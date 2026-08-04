import { useContext, useEffect, useState } from 'react';

import Grid from '@mui/material/Grid';

import Cover from './cover';
import Controls from './controls';
import Display from './display';
import SeekBar from './seekbar';
import Volume from './volume';

import AppSettingsContext from '../../context/appsettings/context';
import PlayerContext from '../../context/player/context';
import request from '../../utils/request';

const Player = () => {
  const { state: { playerstatus } } = useContext(PlayerContext);
  const { cover_url, file, provider } = playerstatus || {};

  const [coverImage, setCoverImage] = useState(undefined);
  const [backgroundImage, setBackgroundImage] = useState('none');

  const {
    settings,
  } = useContext(AppSettingsContext);

  const { show_covers } = settings;

  useEffect(() => {
    const getCoverArt = async () => {
      const { result } = await request('getSingleCoverArt', {
        song_url: file,
        provider,
      });
      if (result) {
        const cover = result.startsWith('http') ? result : `/cover-cache/${result}`;
        setCoverImage(cover);
        setBackgroundImage([
          'linear-gradient(to bottom, rgba(18, 18, 18, 0.5), rgba(18, 18, 18, 1))',
          `url(${cover})`
        ].join(','));
      };
    }

    setCoverImage(undefined);
    setBackgroundImage('none');
    if (cover_url && show_covers) {
      setCoverImage(cover_url);
      setBackgroundImage([
        'linear-gradient(to bottom, rgba(18, 18, 18, 0.5), rgba(18, 18, 18, 1))',
        `url(${cover_url})`
      ].join(','));
    }
    else if (file && show_covers) {
      getCoverArt();
    }
  }, [cover_url, file, provider, show_covers]);

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
        data-testid="player-backdrop"
        size={12}
        sx={{
          paddingTop: '30px',
          paddingLeft: '30px',
          paddingRight: '30px',
          minHeight: 'calc(100vh - 64px - 10px)',
          backdropFilter: 'blur(25px)',
        }}
      >
        <Grid size={{ xs: 12, sm: 5 }}>
          <Cover coverImage={coverImage} />
        </Grid>
        <Grid size={{ xs: 12, sm: 7 }}>
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
