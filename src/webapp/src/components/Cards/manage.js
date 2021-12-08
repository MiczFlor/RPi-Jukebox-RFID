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

import PlayerContext from '../../context/player/context';
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
  const params = useParams();
  const { state } = useContext(PlayerContext);

  console.log(state['rfid.card_id'])

  const [cardId] = useState(
    state['rfid.card_id']
    || params.cardId
    || undefined
    // || "9123134298459334" // For testing purposes only
  );

  const [selectedAction, setSelectedAction] = useState(undefined);
  const [actionData, setActionData] = useState({});

  useEffect(() => {
    const loadCardList = async () => {
      const { result, error } = await request('cardsList');

      if (result && cardId && result[cardId]) {
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

    loadCardList();
  }, [cardId]);

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
