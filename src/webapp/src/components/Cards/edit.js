import React, { useState } from 'react';
import { useHistory } from 'react-router';

import Avatar from '@material-ui/core/Avatar';
import BookmarkIcon from '@material-ui/icons/Bookmark';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import Grid from '@material-ui/core/Grid';

import Header from '../Header';
import ControlsSelector from './controls/controls-selector';
import CardsDeleteDialog from './dialogs/delete';
import { deleteCard, registerCard } from '../../utils/requests';

const CardEdit = () => {
  const history = useHistory();
  const { location: { state } } = history;
  const { action, id, from_quick_select } = state;

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedAction, setSelectedAction] = useState(from_quick_select);
  const [selectedFolder, setSelectedFolder] = useState(action?.args);

  const handleRegisterCard = () => {
    if (selectedFolder) {
      const kwargs = {
        card_id: id,
        quick_select: selectedAction,
        args: selectedFolder,
        overwrite: true,
      };

      return registerCard(kwargs);
    }
  };

  const handleDeleteCard = async () => {
    const { error } = await deleteCard(id);

    if (error) {
      return console.error(error);
    }

    history.push('/cards');
  };

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
              title={id}
            />
            <CardContent>
              <Grid container direction="row" alignItems="center">
                <ControlsSelector
                  selectedAction={selectedAction}
                  setSelectedAction={setSelectedAction}
                  selectedFolder={selectedFolder}
                  setSelectedFolder={setSelectedFolder}
                />
              </Grid>
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
                onClick={handleRegisterCard}
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
        cardId={id}
      />
    </>
  );
};

export default CardEdit;
