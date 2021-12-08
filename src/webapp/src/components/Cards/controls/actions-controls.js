import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router';

import {
  Button,
  CardActions,
} from '@mui/material';

import CardsDeleteDialog from '../dialogs/delete';
import request from '../../../utils/request';

import { JUKEBOX_ACTIONS_MAP } from '../../../config';

const ActionsControls = ({
  actionData,
  cardId,
  selectedAction,
}) => {
  const navigate = useNavigate();
  const { '*': path } = useParams();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const handleRegisterCard = async () => {
    const kwargs = {
      card_id: cardId.toString(),
      cmd_alias: selectedAction,
      overwrite: true,
    };
    const { argKeys = [] } = JUKEBOX_ACTIONS_MAP[selectedAction];

    if (argKeys) {
      kwargs.args = argKeys.map(
        key => actionData[selectedAction][key]
      );
    }

    const { error } = await request('registerCard', kwargs);

    if (error) {
      return console.error(error);
    }

    navigate('../');
  };

  const handleDeleteCard = async () => {
    const { error } = await request('deleteCard', { card_id: cardId });

    // TODO: Better Error handling in frontend
    if (error) {
      return console.error(error);
    }

    navigate('/cards');
  };

  return (
    <>
      <CardActions
        sx={{
          marginTop: '40px',
          justifyContent: path === 'register' ? 'flex-end' : 'space-between'
        }}
      >
        {path !== 'register' &&
          <Button
            color="secondary"
            size="small"
            onClick={() => setDeleteDialogOpen(true)}
          >
            Delete
          </Button>
        }
        <Button
          color="primary"
          onClick={() => handleRegisterCard(cardId)}
          size="small"
        >
          Save
        </Button>
      </CardActions>
      <CardsDeleteDialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        doDelete={handleDeleteCard}
        cardId={cardId}
      />
    </>
  );
};

export default ActionsControls;
