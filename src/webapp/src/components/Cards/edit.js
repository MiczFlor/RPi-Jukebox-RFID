import React, { useEffect, useState } from 'react';
import { useHistory, useParams } from 'react-router';

import Avatar from '@mui/material/Avatar';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import CircularProgress from '@mui/material/CircularProgress';
import Grid from '@mui/material/Grid';

import Header from '../Header';
import ControlsSelector from './controls/controls-selector';
import CardsDeleteDialog from './dialogs/delete';
import request from '../../utils/request';

const CardEdit = () => {
  const history = useHistory();
  const params = useParams();
  const { location: { state } } = history;

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [cardId, setCardId] = useState(undefined);
  const [selectedAction, setSelectedAction] = useState(undefined);
  const [selectedAlbum, setSelectedAlbum] = useState(undefined);
  const [isLoading, setIsLoading] = useState(false);

  const handleRegisterCard = async (card_id) => {
    const kwargs = {
      card_id: card_id.toString(),
      cmd_alias: selectedAction,
      overwrite: true,
    };

    if (selectedAction === 'play_album') {
      const { albumartist, album } = selectedAlbum;
      kwargs.args = [albumartist, album];
    }

    const { error } = await request('registerCard', kwargs);

    if (error) {
      return console.error(error);
    }

    history.push('/cards');
  };

  const handleDeleteCard = async () => {
    const { error } = await request('deleteCard', { card_id: cardId });

    // TODO: Better Error handling in frontend
    if (error) {
      return console.error(error);
    }

    history.push('/cards');
  };

  useEffect(() => {
    if (state && state.id) {
      setCardId(state.id);
      setSelectedAction(state.from_alias);
      const [ albumartist, album ] = state.action?.args || [];
      setSelectedAlbum({ albumartist, album });
      return;
    }

    const loadCardList = async () => {
      setIsLoading(true);
      const { result, error } = await request('cardsList');
      setIsLoading(false);

      if (result && params?.cardId && result[params.cardId]) {
        setCardId(params.cardId);
        setSelectedAction(result[params.cardId].from_alias);
        const [ albumartist, album ] = result[params.cardId].action?.args || [];
        setSelectedAlbum({ albumartist, album });
      }

      if (error) {
        console.error(error);
        history.push('/cards');
      }
    }

    loadCardList();
  }, [history, params, state]);

  return (
    <>
      <Header title="Edit Card" backLink="/cards" />
      <Grid container>
        <Grid item xs={12}>
          <Card elevation={0}>
            <CardHeader
              avatar={
                <Avatar aria-label="Card Icon">
                  <BookmarkIcon />
                </Avatar>
              }
              title={cardId}
            />
            <CardContent>
              {isLoading
                ? <CircularProgress />
                : <Grid container direction="row" alignItems="center">
                    <ControlsSelector
                      selectedAction={selectedAction}
                      setSelectedAction={setSelectedAction}
                      selectedAlbum={selectedAlbum}
                      setSelectedAlbum={setSelectedAlbum}
                    />
                  </Grid>
              }
            </CardContent>
            <CardActions>
              <Button
                color="secondary"
                size="small"
                onClick={(e) => setDeleteDialogOpen(true)}
              >
                Delete
              </Button>
              <Button
                size="small"
                color="primary"
                onClick={(e) => handleRegisterCard(cardId)}
              >
                Save
              </Button>
            </CardActions>
          </Card>
        </Grid>
      </Grid>
      <CardsDeleteDialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        doDelete={handleDeleteCard}
        cardId={cardId}
      />
    </>
  );
};

export default CardEdit;
