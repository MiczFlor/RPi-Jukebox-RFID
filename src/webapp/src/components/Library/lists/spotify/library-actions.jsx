import { useTranslation } from 'react-i18next';

import {
  Box,
  Button,
} from '@mui/material';

import AddLinkIcon from '@mui/icons-material/AddLink';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';

const actionButtonSx = {
  minHeight: 44,
  minWidth: 44,
};

const SpotifyLibraryActions = ({
  isSelecting,
  onAdd,
  onCancelSelection,
  onDeleteSelected,
  onStartSelection,
  selectedCount,
}) => {
  const { t } = useTranslation();

  return (
    <Box
      aria-label={t('library.spotify.manager.actions-label')}
      role="toolbar"
      sx={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: 1,
        justifyContent: { xs: 'stretch', sm: 'flex-start' },
        marginBottom: 1,
        width: '100%',
        '& > button': {
          flex: { xs: '1 1 auto', sm: '0 0 auto' },
        },
      }}
    >
      {isSelecting
        ? <>
            <Button
              color="error"
              disabled={selectedCount === 0}
              onClick={onDeleteSelected}
              startIcon={<DeleteIcon />}
              sx={actionButtonSx}
              variant="contained"
            >
              {t('library.spotify.manager.delete-selected', {
                count: selectedCount,
              })}
            </Button>
            <Button
              onClick={onCancelSelection}
              startIcon={<CloseIcon />}
              sx={actionButtonSx}
              variant="outlined"
            >
              {t('general.buttons.cancel')}
            </Button>
          </>
        : <>
            <Button
              onClick={onAdd}
              startIcon={<AddLinkIcon />}
              sx={actionButtonSx}
              variant="contained"
            >
              {t('library.spotify.manager.add')}
            </Button>
            <Button
              onClick={onStartSelection}
              startIcon={<CheckBoxIcon />}
              sx={actionButtonSx}
              variant="outlined"
            >
              {t('library.spotify.manager.select')}
            </Button>
          </>
      }
    </Box>
  );
};

export default SpotifyLibraryActions;
