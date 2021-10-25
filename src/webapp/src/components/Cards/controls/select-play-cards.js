import React, { useEffect, useState } from 'react';

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

  return (
    <FormControl>
      <NativeSelect
        value={selectedAlbum || '0'}
        onChange={handleAlbumChange}
        name="albums"
        inputProps={{ 'aria-label': 'Albums' }}
      >
        {isLoading
          ? <option key={0} value={'0'} disabled={true}>Loading</option>
          : <option key={0} value={'0'} disabled={true}>Select an album</option>
        }
        {error && <option key={0} value={'0'} disabled={true}>An error occurred loading the library.</option>}
        {albums.map(({ album }, i) =>
          <option key={i} value={album}>
            {album || LABELS.UNKNOW_ALBUM}
          </option>
        )}
      </NativeSelect>
    </FormControl>
  );
};

export default SelectPlayCards;
