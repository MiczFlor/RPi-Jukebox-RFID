import { useTranslation } from 'react-i18next';

import {
  Checkbox,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Tooltip,
} from '@mui/material';

import NavigateNextIcon from '@mui/icons-material/NavigateNext';

import request from '../../../../utils/request';
import FolderLink from './folder-link';
import FolderTypeAvatar from './folder-type-avatar';

const FolderListItem = ({
  folder,
  isManagementSelecting,
  isSelecting,
  isSelected,
  onToggleSelected,
  registerMusicToCard,
}) => {
  const { t } = useTranslation();
  const { type, name, relpath } = folder;

  const playItem = () => {
    switch(type) {
      case 'directory': return request('play_folder', { folder: relpath, recursive: true });
      case 'file': return request('play_single', { song_url: relpath });
      // TODO: Add missing Podcast
      // TODO: Add missing Stream
      default: return;
    }
  }

  const registerItemToCard = () => {
    switch(type) {
      case 'directory': return registerMusicToCard('play_folder', { folder: relpath, recursive: true });
      case 'file': return registerMusicToCard('play_single', { song_url: relpath });
      // TODO: Add missing Podcast
      // TODO: Add missing Stream
      default: return;
    }
  }

  const activateItem = () => {
    if (isManagementSelecting) return onToggleSelected(folder);
    if (isSelecting) return registerItemToCard();
    return playItem();
  };

  const secondaryAction = !isManagementSelecting && type === 'directory'
    ? <Tooltip title={t('library.folders.show-folder-content')}>
        <IconButton
          aria-label={t('library.folders.show-folder-content')}
          component={FolderLink}
          data={{ dir: relpath }}
          edge="end"
          nativeButton={false}
          sx={{ height: 44, width: 44 }}
        >
          <NavigateNextIcon />
        </IconButton>
      </Tooltip>
    : undefined;

  return (
    <ListItem
      disablePadding
      secondaryAction={secondaryAction}
    >
      <ListItemButton
        onClick={activateItem}
        selected={isManagementSelecting && isSelected}
        sx={{ minHeight: 56 }}
      >
        {isManagementSelecting &&
          <ListItemIcon sx={{ minWidth: 44 }}>
            <Checkbox
              checked={isSelected}
              edge="start"
              slotProps={{
                input: {
                  'aria-label': t('library.folders.manager.select-item', { name }),
                },
              }}
              tabIndex={-1}
            />
          </ListItemIcon>
        }
        <FolderTypeAvatar type={type} />
        <ListItemText
          primary={name}
          slotProps={{
            primary: {
              sx: { overflowWrap: 'anywhere' },
            },
          }}
        />
      </ListItemButton>
    </ListItem>
  );
}

export default FolderListItem;
