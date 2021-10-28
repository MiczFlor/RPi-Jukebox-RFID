import React, { useEffect, useState } from 'react';
import { findIndex, propEq } from 'ramda';

import {
  FormControl,
  NativeSelect
} from '@mui/material';

import request from '../../../utils/request';
import { flatByAlbum } from '../../../utils/utils';
import { LABELS } from '../../../config';

const SelectPlayCards = ({
  selectedAlbum,
  handleAlbumChange
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
    const album = {
      index: event.target?.value,
      ...albums[event.target?.value]
    }

    handleAlbumChange(album);
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
    <FormControl>
      <NativeSelect
        value={findSelectedIndexAsValue(selectedAlbum || {})}
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
  );
};

export default SelectPlayCards;
