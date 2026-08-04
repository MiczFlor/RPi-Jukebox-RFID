import { useTranslation } from 'react-i18next';

import {
  Button,
  Grid,
  IconButton,
} from '@mui/material';

import PlayCircleFilledRoundedIcon from '@mui/icons-material/PlayCircleFilledRounded';
import request from '../../../../../utils/request';

const SongListControls = ({
  albumartist,
  album,
  contentUri,
  disabled,
  registerMusicToCard,
  isSelecting,
  provider,
}) => {
  const { t } = useTranslation();
  const command = 'play_album';

  const playAlbum = () => (
    request(command, {
      albumartist,
      album,
      content_uri: contentUri,
      provider,
    })
  );

  const registerAlbumToCard = () => (
    registerMusicToCard(command, {
      albumartist,
      album,
      content_uri: contentUri,
      provider,
    })
  );

  return (
    <Grid container size={12} sx={{ padding: '0 8px' }}>
      <Grid size={12}
        sx={{
          display: 'flex',
          justifyContent: 'right',
        }}
      >
        {
          !isSelecting
            ? <IconButton
                aria-label="Play"
                onClick={playAlbum}
                disabled={disabled}
                size="large"
              >
                <PlayCircleFilledRoundedIcon color="primary" style={{ fontSize: 64 }} />
              </IconButton>
            : <Button
                variant="outlined"
                onClick={registerAlbumToCard}
                sx={{ margin: '20px 0 4px' }}
              >
                {t('library.albums.assign-to-card')}
              </Button>
        }
      </Grid>
    </Grid>
  );
};

export default SongListControls;
