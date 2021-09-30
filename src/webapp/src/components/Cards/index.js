import React, { useEffect, useState } from 'react';
import { useHistory } from 'react-router';

import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';

import AddIcon from '@material-ui/icons/Add';
import CardsList from './cardslist';
import Fab from '@material-ui/core/Fab';
import Header from '../Header';
import { socketRequest } from '../../sockets';

const useStyles = makeStyles((theme) => ({
  cardsList: {
    display: 'flex',
    justifyContent: 'center',
  },
  fab: {
    position: 'fixed',
    bottom: theme.spacing(2) + 60,
    right: theme.spacing(2),
  },
}));

const Cards = () => {
  const classes = useStyles();

  const [data, setData] = useState({});
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const history = useHistory();

  const openEditCard = (data) => {
    history.push(`/cards/${data.id}/edit`, data);
  };

  const openRegisterCard = () => {
    history.push('/cards/register');
  };

  useEffect(() => {
    const fetchCardsList = async () => {
      setIsLoading(true);

      try {
        const result = await socketRequest('cards', 'list_cards');
        setData(result);
      }
      catch (error) {
        setError(error)
      };

      setIsLoading(false);
    };

    fetchCardsList();
  }, [history]);

  return (
    <div id="cards">
      <Header title="Cards" />
      <Grid container spacing={1} className={classes.cardsList}>
        {isLoading
          ? <CircularProgress />
          : <CardsList
              cardsList={data}
              openEditCard={openEditCard}
            />
        }
        {error &&
          <Typography>An error occurred while loading cards list.</Typography>
        }
      </Grid>
      <Fab
        aria-label="Register card"
        className={classes.fab}
        color="primary"
        onClick={openRegisterCard}
      >
        <AddIcon />
      </Fab>
    </div>
  );
};

export default Cards;
