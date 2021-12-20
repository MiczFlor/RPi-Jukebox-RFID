import React from 'react';

import {
  Avatar,
  Card,
  CardContent,
  CardHeader,
  Grid,
  Typography
} from '@mui/material';
import BookmarkIcon from '@mui/icons-material/Bookmark';

import Header from '../Header';
import ActionsControls from './controls/actions-controls';
import ControlsSelector from './controls/controls-selector';

const InfoNoCardSwiped = () => (
  <Typography>
    ⚠️ Please swipe a card to recieve an ID which will
    be used to register a new action.
  </Typography>
);

const CardsForm = ({
  title,
  cardId,
  actionData,
  setActionData,
}) => (
  <>
    <Header title={title} backLink="/cards" />
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
                    actionData={actionData}
                    setActionData={setActionData}
                    cardId={cardId}
                  />
                </Grid>
                <ActionsControls
                  actionData={actionData}
                  cardId={cardId}
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



export default CardsForm;
