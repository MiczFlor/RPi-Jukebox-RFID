import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  Button,
} from '@mui/material';

import CheckBoxIcon from '@mui/icons-material/CheckBox';
import CloseIcon from '@mui/icons-material/Close';
import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder';
import DeleteIcon from '@mui/icons-material/Delete';
import DriveFolderUploadIcon from '@mui/icons-material/DriveFolderUpload';
import UploadFileIcon from '@mui/icons-material/UploadFile';

import { ACCEPTED_LIBRARY_FILES } from '../../../../utils/library-api';
import { createUploadSelection } from './upload-selection';

const actionButtonSx = {
  minHeight: 44,
  minWidth: 44,
};

const LibraryActions = ({
  isSelecting,
  selectedCount,
  onCancelSelection,
  onCreateFolder,
  onDeleteSelected,
  onStartSelection,
  onUploadSelected,
}) => {
  const { t } = useTranslation();

  const selectFiles = (event) => {
    const files = Array.from(event.target.files || []);
    event.target.value = '';
    if (files.length) onUploadSelected(createUploadSelection(files));
  };

  const selectFolders = (event) => {
    const files = Array.from(event.target.files || []);
    event.target.value = '';
    if (files.length) onUploadSelected(createUploadSelection(files));
  };

  return (
    <Box
      aria-label={t('library.folders.manager.actions-label')}
      role="toolbar"
      sx={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: 1,
        justifyContent: { xs: 'stretch', sm: 'flex-start' },
        marginBottom: 1,
        width: '100%',
        '& > button, & > label': {
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
              {t('library.folders.manager.delete-selected', { count: selectedCount })}
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
              component="label"
              role="button"
              startIcon={<UploadFileIcon />}
              sx={actionButtonSx}
              variant="contained"
            >
              {t('library.folders.manager.upload-files')}
              <input
                accept={ACCEPTED_LIBRARY_FILES}
                hidden
                multiple
                onChange={selectFiles}
                type="file"
              />
            </Button>
            <Button
              component="label"
              role="button"
              startIcon={<DriveFolderUploadIcon />}
              sx={actionButtonSx}
              variant="contained"
            >
              {t('library.folders.manager.upload-folders')}
              <input
                accept={ACCEPTED_LIBRARY_FILES}
                directory=""
                hidden
                multiple
                onChange={selectFolders}
                type="file"
                webkitdirectory=""
              />
            </Button>
            <Button
              onClick={onCreateFolder}
              startIcon={<CreateNewFolderIcon />}
              sx={actionButtonSx}
              variant="outlined"
            >
              {t('library.folders.manager.create-folder')}
            </Button>
            <Button
              onClick={onStartSelection}
              startIcon={<CheckBoxIcon />}
              sx={actionButtonSx}
              variant="outlined"
            >
              {t('library.folders.manager.select')}
            </Button>
          </>
      }
    </Box>
  );
};

export default LibraryActions;
