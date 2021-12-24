import React from 'react';

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

import { JUKEBOX_ACTIONS_MAP } from '../../../../../config';
import { getActionAndCommand, getArgsValues } from '../../../utils';

import SelectedAlbum from './selected-album';
import SelectedFolder from './selected-folder';
import SelectedSingle from './selected-single';

const SelectPlayMusic = ({
  actionData,
  cardId,
}) => {
  const navigate = useNavigate();

  const { action, command } = getActionAndCommand(actionData);
  const commandTitle = command && JUKEBOX_ACTIONS_MAP[action].commands[command]?.title;
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
          <Typography>{`Selected ${commandTitle}`}</Typography>
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
          Select music
        </Button>
      </Grid>
    </Grid>
  );
};

export default SelectPlayMusic;
