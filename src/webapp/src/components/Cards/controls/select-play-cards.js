import React, { useEffect, useState } from 'react';

import {
  FormControl,
  NativeSelect
} from '@mui/material';

import {
  getFlattenListOfDirectories
} from '../../../utils/requests';

const SelectPlayCards = ({
  selectedFolder,
  handleFolderChange
}) => {
  const [folders, setFolders] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      setFolders(await getFlattenListOfDirectories());
    };

    fetchData();
  }, []);

  return (
    <FormControl>
      <NativeSelect
        value={selectedFolder || '0'}
        onChange={handleFolderChange}
        name="folders"
        inputProps={{ 'aria-label': 'Folders' }}
      >
        <option key={0} value={'0'} disabled={true}>Select a folder</option>
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
