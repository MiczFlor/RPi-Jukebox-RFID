import React, { useEffect, useState } from 'react';

import {
  FormControl,
  NativeSelect
} from '@mui/material';

import {
  fetchDirectoryTreeOfAudiofolder
} from '../../../utils/requests';

const SelectPlayCards = ({
  selectedFolder,
  handleFolderChange
}) => {
  const [folders, setFolders] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getFlattenListOfDirectories = async () => {
      setIsLoading(true);
      const { result, error } = await fetchDirectoryTreeOfAudiofolder();
      setIsLoading(false);

      if(result) setFolders(result.filter(entry => !!entry.directory));
      if(error) setError(error);
    }

    getFlattenListOfDirectories();
  }, []);

  return (
    <FormControl>
      <NativeSelect
        value={selectedFolder || '0'}
        onChange={handleFolderChange}
        name="folders"
        inputProps={{ 'aria-label': 'Folders' }}
      >
        {isLoading
          ? <option key={0} value={'0'} disabled={true}>Loading</option>
          : <option key={0} value={'0'} disabled={true}>Select a folder</option>
        }
        {error && <option key={0} value={'0'} disabled={true}>An error occurred loading the library.</option>}
        {folders.map((folder, i) =>
          <option key={i} value={folder.directory}>
            {folder.directory}
          </option>
        )}
      </NativeSelect>
    </FormControl>
  );
};

export default SelectPlayCards;
