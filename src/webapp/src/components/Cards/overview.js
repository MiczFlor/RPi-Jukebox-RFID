import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';

import AddIcon from '@mui/icons-material/Add';
import CardsList from './list';
import CircularProgress from '@mui/material/CircularProgress';
import Fab from '@mui/material/Fab';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import Header from '../Header';
import request from '../../utils/request';

const CardsOverview = () => {
  const navigate = useNavigate();
  const theme = useTheme();

  const [data, setData] = useState({});
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const openRegisterCard = () => {
    navigate('register');
  };

  useEffect(() => {
    const loadCardList = async () => {
      setIsLoading(true);
      const { result, error } = await request('cardsList');
      setIsLoading(false);

      if(result) setData(result);
      if(error) setError(error);
    }

    loadCardList();
  }, []);

  return (
    <Grid container id="cards">
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
    </Grid>
  );
};

export default CardsOverview;
