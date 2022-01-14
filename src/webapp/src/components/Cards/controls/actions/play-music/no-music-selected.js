import React from 'react';
import { useTranslation } from 'react-i18next';

import { Typography } from '@mui/material';

const NoMusicSelected = () => {
  const { t } = useTranslation();

  return (
    <Typography>
      {t('cards.controls.actions.play-music.no-music-selected')}
    </Typography>
  );
}

export default NoMusicSelected;
