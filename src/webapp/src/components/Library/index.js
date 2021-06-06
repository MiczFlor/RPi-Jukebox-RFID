import React, { useEffect, useState } from 'react';

import {
  Card,
  CardContent,
  CardMedia,
  CircularProgress,
  makeStyles,
  TextField
} from '@material-ui/core';

import { socketRequest } from '../../sockets';
import { preparePayload } from '../../sockets/utils';
import noCover from '../../assets/noCover.jpg';

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    marginTop: '10px',
  },
  content: {
    flex: '1 0 auto',
  },
  cover: {
    width: 100,
    height: 100,
  },
}));

const FolderCard = ({ classes, folder }) => {
  const { label } = folder;

  return (
    <Card className={classes.root} variant="outlined">
      <CardMedia className={classes.cover} image={noCover}></CardMedia>
      <CardContent className={classes.content}>{label}</CardContent>
    </Card>
  );
};

const Library = () => {
  const classes = useStyles();

  const [isLoading, setIsLoading] = useState(true);
  const [folders, setFolders] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (event) => {
    setSearchQuery(event.target.value);
  };

  const labelBySearchQuery = ({ label }) => {
    if (searchQuery === '') return true;
    return label.includes(searchQuery);
  };

  useEffect(() => {
    const getFlattenListOfFolders = async () => {
      const payload = preparePayload('filesystem', 'get_all_folders_flattened', {});
      const { folders = [] } = await socketRequest(payload);

      setFolders(folders);
    };

    getFlattenListOfFolders();
    setIsLoading(false);
  }, [isLoading]);

  return (
    <div id="library">
      <form noValidate autoComplete="off">
        <TextField
          id="outlined-basic"
          label="Search"
          variant="outlined"
          value={searchQuery}
          onChange={handleSearch}
        />
      </form>
      {isLoading && <CircularProgress />}
      {
        !isLoading &&
        folders
          .filter(labelBySearchQuery)
          .map((folder) =>
            <FolderCard
              key={folder.path}
              folder={folder}
              classes={classes}
            />
          )
      }
    </div>
  );
};

export default Library;
