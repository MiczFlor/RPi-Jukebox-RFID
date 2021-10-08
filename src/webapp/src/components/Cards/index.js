import React, { useEffect, useState } from 'react';
import { useHistory } from 'react-router';

import AddIcon from '@mui/icons-material/Add';
import CardsList from './cardslist';
import CircularProgress from '@mui/material/CircularProgress';
import Fab from '@mui/material/Fab';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import Header from '../Header';
import { fetchCardsList } from '../../utils/requests';

const Cards = () => {
  const history = useHistory();
  const theme = useTheme();

  const [data, setData] = useState({});
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const openRegisterCard = () => {
    history.push('/cards/register');
  };

  useEffect(() => {
    const loadCardList = async () => {
      const { result, error } = await fetchCardsList(setIsLoading);

      if(result) setData(result);
      if(error) setError(error);
    }

    loadCardList();
  }, [history]);

  return (
    <div id="cards">
      <Header title="Cards" />
      <Grid
        container
        spacing={1}
        sx={{
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        {isLoading
          ? <CircularProgress />
          : <CardsList cardsList={data} />
        }
        {error &&
          <Typography>An error occurred while loading cards list.</Typography>
        }
      </Grid>
      <Fab
        aria-label="Register card"
        color="primary"
        onClick={openRegisterCard}
        sx={{
          position: 'fixed',
          bottom: '76px',
          right: theme.spacing(2),
        }}
      >
        <AddIcon />
      </Fab>
    </div>
  );
};

export default Cards;
