import React, { useContext, useEffect, useState } from 'react';
import { useHistory } from 'react-router';

import {
  Avatar,
  Button,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  Grid,
  Typography
} from '@material-ui/core';
import BookmarkIcon from '@material-ui/icons/Bookmark';

import PlayerContext from '../../context/player/context';

import Header from '../Header';
import ControlsSelector from './controls/controls-selector';
import { registerCard } from '../../utils/requests';

const InfoNoCardSwiped = () => (
  <Typography>
    ⚠️ Please swipe a card to recieve and ID which will
    be used to register a new action.
  </Typography>
);

const ActionsControls = ({
  handleRegisterCard,
}) => {
  return (
    <CardActions>
      <Button
        color="primary"
        onClick={handleRegisterCard}
        size="small"
      >
        Save
      </Button>
    </CardActions>
  );
};

const CardsRegister = () => {
  const history = useHistory();
  const { state } = useContext(PlayerContext);

  const { 'rfid.card_id': card_id } = state;

  const [lastSwipedCardId, setLastSwipedCardId] = useState(card_id || undefined);
  const [selectedAction, setSelectedAction] = useState(undefined);
  const [selectedFolder, setSelectedFolder] = useState(undefined);

  const handleRegisterCard = async () => {
    if (selectedFolder) {
      const kwargs = {
        card_id: lastSwipedCardId.toString(),
        quick_select: selectedAction,
        args: selectedFolder,
        overwrite: true,
      };

      const { error } = await registerCard(kwargs);

      if (error) {
        return console.error(error);
      }

      history.push('/cards');
    }
  };

  useEffect(() => {
    console.log(`setLastSwipedCardId(${card_id});`);
    setLastSwipedCardId(card_id);
  }, [card_id])

  return (
    <>
      <Header title="Register Card" backLink="/cards" />
      <Grid container>
        <Grid item xs={12}>
          <Card elevation={0}>
            <CardHeader
              avatar={
                <Avatar aria-label="Card Icon">
                  <BookmarkIcon />
                </Avatar>
              }
              title={
                lastSwipedCardId
                  ? lastSwipedCardId
                  : 'No card id'
              }
            />
            <CardContent>
              {lastSwipedCardId &&
                <Grid container direction="row" alignItems="center">
                  <ControlsSelector
                    selectedAction={selectedAction}
                    setSelectedAction={setSelectedAction}
                    selectedFolder={selectedFolder}
                    setSelectedFolder={setSelectedFolder}
                  />
                </Grid>
              }
              {!lastSwipedCardId && <InfoNoCardSwiped />}
            </CardContent>
            {lastSwipedCardId && <ActionsControls
              handleRegisterCard={handleRegisterCard}
            />}
          </Card>
        </Grid>
      </Grid>
    </>
  );
};

export default CardsRegister;
