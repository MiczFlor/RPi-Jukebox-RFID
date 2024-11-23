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

const SelectPlayContent = ({
  actionData,
  cardId,
}) => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const { content_type } = actionData.command.args || {};

  const values = getArgsValues(actionData);

  const selectContent = () => {
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
      {content_type &&
        <Grid item xs={12}>
          <Typography>
            {t(`cards.controls.actions.play-content.commands.${content_type}`)}
          </Typography>
        </Grid>
      }
      <Grid item xs={12}>
        {content_type === 'album' && <SelectedAlbum values={values} />}
        {content_type === 'folder' && <SelectedFolder values={values} />}
        {content_type === 'single' && <SelectedSingle values={values} />}
      </Grid>

      <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'center' }}>
        <Button
          variant="outlined"
          onClick={selectContent}
          endIcon={<KeyboardArrowRightIcon />}
        >
          {t('cards.controls.actions.play-content.button-label')}
        </Button>
      </Grid>
    </Grid>
  );
};

export default SelectPlayContent;
