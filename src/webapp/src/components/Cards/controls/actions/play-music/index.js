import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  createSearchParams,
  useNavigate,
} from 'react-router-dom';

import {
  Button,
  Grid,
  Typography,
} from '@mui/material';

import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';

import { getActionAndCommand, getArgsValues } from '../../../utils';

import SelectedAlbum from './selected-album';
import SelectedFolder from './selected-folder';
import SelectedSingle from './selected-single';

const SelectPlayMusic = ({
  actionData,
  cardId,
}) => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const { command } = getActionAndCommand(actionData);
  const values = getArgsValues(actionData);

  const selectMusic = () => {
    const searchParams = createSearchParams({
      isSelecting: true,
      cardId
    });

    navigate({
      pathname: '/library',
      search: `?${searchParams}`,
   });
  };

  return (
    <Grid container>
      {command &&
        <Grid item xs={12}>
          <Typography>
            {t(`cards.controls.actions.play-music.commands.${command}`)}
          </Typography>
        </Grid>
      }
      <Grid item xs={12}>
        {command === 'play_album' && <SelectedAlbum values={values} />}
        {command === 'play_folder' && <SelectedFolder values={values} />}
        {command === 'play_single' && <SelectedSingle values={values} />}
      </Grid>

      <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'center' }}>
        <Button
          variant="outlined"
          onClick={selectMusic}
          endIcon={<KeyboardArrowRightIcon />}
        >
          {t('cards.controls.actions.play-music.button-label')}
        </Button>
      </Grid>
    </Grid>
  );
};

export default SelectPlayMusic;
