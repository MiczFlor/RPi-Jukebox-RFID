import React, { useContext, useEffect, useState } from 'react';
import { useParams } from 'react-router';

import {
  Avatar,
  Card,
  CardContent,
  CardHeader,
  Grid,
  Typography
} from '@mui/material';
import BookmarkIcon from '@mui/icons-material/Bookmark';

import PubSubContext from '../../context/pubsub/context';
import Header from '../Header';
import ActionsControls from './controls/actions-controls';
import ControlsSelector from './controls/controls-selector';

import request from '../../utils/request';

import { JUKEBOX_ACTIONS_MAP } from '../../config';

const InfoNoCardSwiped = () => (
  <Typography>
    ⚠️ Please swipe a card to recieve and ID which will
    be used to register a new action.
  </Typography>
);

const CardsManage = () => {
  const {
    '*': path,
    cardId: paramsCardId
  } = useParams();
  const { state, setState } = useContext(PubSubContext);
  const { 'rfid.card_id': swipedCardId } = state;
  console.log(state)

  const [cardId, setCardId] = useState(
    paramsCardId
    || swipedCardId
    || undefined
    // || "9123134298459334" // For testing purposes only
  );

  const [selectedAction, setSelectedAction] = useState(undefined);
  const [actionData, setActionData] = useState({});

  // Edit
  useEffect(() => {
    const loadCardList = async () => {
      if (cardId) {
        const { result, error } = await request('cardsList');

        if (result && result[cardId]) {
          const {
            action: { args },
            from_alias: action
          } = result[cardId];
          const { argKeys = [] } = JUKEBOX_ACTIONS_MAP[action];

          setSelectedAction(action);
          const values = argKeys.reduce((prev, arg, position) => (
            {
              ...prev,
              [arg]: args[position],
            }
          ), {});

          setActionData({ [action]: values });
        }

        if (error) {
          console.error(error);
        }
      }
    }

    loadCardList();
  }, [cardId]);

  // Register
  useEffect(() => {
    setCardId(paramsCardId || swipedCardId);
  }, [paramsCardId, swipedCardId])

  return (
    <>
      <Header title="Card Manager" backLink="/cards" />
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
                cardId
                  ? cardId
                  : 'No card id'
              }
            />
            <CardContent>
              {cardId &&
                <>
                  <Grid container direction="row" alignItems="center">
                    <ControlsSelector
                      selectedAction={selectedAction}
                      setSelectedAction={setSelectedAction}
                      actionData={actionData}
                      setActionData={setActionData}
                    />
                  </Grid>
                  <ActionsControls
                    actionData={actionData}
                    cardId={cardId}
                    selectedAction={selectedAction}
                  />
                </>
              }
              {!cardId && <InfoNoCardSwiped />}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </>
  );
};

export default CardsManage;
