import React, { useEffect, useState, useContext } from 'react';

import {
  Button,
  Card,
  CardContent,
  CardMedia,
  CircularProgress,
  Grid,
  makeStyles,
  TextField,
  Typography
} from '@material-ui/core';

import { socketRequest } from '../../sockets';
import noCover from '../../assets/noCover.jpg';
import PlayerContext from '../../context/player/context';

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    height: '100%'
  },
  content: {
    flex: '1',
  },
  cover: {
    width: 100,
    height: 100,
  },
  searchInput: {
    width: '100%',
    marginBottom: 10,
  }
}));

const DirectoryCard = ({ classes, directory, play }) => {
  const tree = directory.split('/');
  const folder = tree.pop();
  const parentPath = tree.join('/');

  return (
    <Grid item xs={12} sm={6}>
      <Card className={classes.root} variant="outlined">
        <CardMedia className={classes.cover} image={noCover}></CardMedia>
        <CardContent className={classes.content}>
          <Typography variant="subtitle1" display="block" gutterBottom>{folder}</Typography>
          <Typography variant="overline" display="block" gutterBottom>{parentPath}</Typography>
          <Button variant="outlined" onClick={e => play(directory)}>Play</Button>
        </CardContent>
      </Card>
    </Grid>
  );
};

const Library = () => {
  const classes = useStyles();
  const {
    play,
    state: { playerstatus },
  } = useContext(PlayerContext);

  const [isLoading, setIsLoading] = useState(true);
  const [folders, setFolders] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (event) => {
    setSearchQuery(event.target.value);
  };

  const directoryNameBySearchQuery = ({ directory }) => {
    if (searchQuery === '') return true;
    return directory.toLowerCase().includes(searchQuery.toLowerCase());
  };

  useEffect(() => {
    const getFlattenListOfDirectories = async () => {
      const list = await socketRequest('player', 'list_all_dirs');

      setFolders(list.filter(entry => !!entry.directory));
    };

    getFlattenListOfDirectories();
    setIsLoading(false);
  }, []);

  return (
    <div id="library">
      <form noValidate autoComplete="off">
        <Grid container>
          <Grid item xs={12}>
            <TextField
              className={classes.searchInput}
              id="outlined-basic"
              label="Search"
              variant="outlined"
              value={searchQuery}
              onChange={handleSearch}
            />
          </Grid>
        </Grid>
      </form>
      {isLoading && <CircularProgress />}
      {
        !isLoading &&
        <Grid container spacing={1}>
        {
          folders
            .filter(directoryNameBySearchQuery)
            .map(({ directory }) =>
              <DirectoryCard
                classes={classes}
                directory={directory}
                key={directory}
                play={play}
                playerstatus={playerstatus}
              />
            )
        }
        </Grid>
      }
      {/* {
        !isLoading &&
        !folders.filter(directoryNameBySearchQuery).length &&
        <Typography variant="overline" display="block" gutterBottom>Nothing found</Typography>
      } */}
    </div>
  );
};

export default Library;
