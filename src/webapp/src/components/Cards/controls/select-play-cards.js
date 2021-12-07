import React, { useEffect, useState } from 'react';
import { findIndex, propEq } from 'ramda';

import {
  FormControl,
  Grid,
  NativeSelect,
  Typography,
} from '@mui/material';

import request from '../../../utils/request';
import { flatByAlbum } from '../../../utils/utils';
import { LABELS } from '../../../config';

const SelectPlayCards = ({
  actionData,
  handleActionDataChange,
}) => {
  const [albums, setAlbums] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAlbumList = async () => {
      setIsLoading(true);
      const { result, error } = await request('albumList');
      setIsLoading(false);

      if(result) setAlbums(result.reduce(flatByAlbum, []));
      if(error) setError(error);
    }

    fetchAlbumList();
  }, []);

  const onChange = (event) => {
    const values = {
      index: event.target?.value,
      ...albums[event.target?.value]
    }

    handleActionDataChange('play_album', values);
  }

  const findSelectedIndexAsValue = ({ albumartist, album }) => {
    const index = findIndex(
      propEq('albumartist', albumartist) &&
      propEq('album', album)
    )(albums);

    if (index === -1) return 'label';
    return index;
  }

  return (
    <Grid container direction="row" alignItems="center">
      <Grid item xs={5}>
        <Typography>Albums</Typography>
      </Grid>
      <Grid item xs={7}>
        <FormControl>
          <NativeSelect
            value={findSelectedIndexAsValue(actionData.play_album || {})}
            onChange={onChange}
            name="albums"
            inputProps={{ 'aria-label': 'Albums' }}
          >
            {isLoading
              ? <option key={'label'} value={'label'} disabled={true}>Loading</option>
              : <option key={'label'} value={'label'} disabled={true}>Select an album</option>
            }
            {error && <option key={'label'} value={'label'} disabled={true}>An error occurred loading the library.</option>}
            {albums.map(({ album }, key) =>
              <option key={key} value={key}>
                {album || LABELS.UNKNOW_ALBUM}
              </option>
            )}
          </NativeSelect>
        </FormControl>
      </Grid>
    </Grid>
  );
};

export default SelectPlayCards;
