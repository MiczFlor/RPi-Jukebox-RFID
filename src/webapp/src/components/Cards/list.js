import React, { forwardRef } from 'react';
import { Link } from 'react-router-dom';
import { isNil, reject } from 'ramda';
import { useTranslation } from 'react-i18next';

import {
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Typography
} from '@mui/material';

import BookmarkIcon from '@mui/icons-material/Bookmark';
import { printObject } from '../../utils/utils';

const CardsList = ({ cardsList }) => {
  const { t } = useTranslation();

  const ListItemLink = (cardId) => {
    const EditCardLink = forwardRef((props, ref) => {
      const { data } = props;
      const location = {
        pathname: `/cards/${data.id}/edit`,
        state: data,
      };

      return <Link ref={ref} to={location} {...props} />
    });

    const command = cardsList[cardId].from_alias === 'play_from_reader' ? 'play_content' : cardsList[cardId].from_alias;

    const description = command
      ? reject(
          isNil,
          [
            t(`cards.controls.command-selector.commands.${command}`),
            printObject(cardsList[cardId].action.args)
          ]
        ).join(', ')
      : cardsList[cardId].func

    return (
      <ListItem
        button
        component={EditCardLink}
        data={{ id: cardId, ...cardsList[cardId] }}
        key={cardId}
      >
        <ListItemAvatar>
          <Avatar>
            <BookmarkIcon />
          </Avatar>
        </ListItemAvatar>
        <ListItemText
          primary={cardId}
          secondary={description}
        />
      </ListItem>
    );
  }

  return (
    cardsList && Object.keys(cardsList).length > 0
      ? <List sx={{ width: '100%' }}>
          {Object.keys(cardsList).map(ListItemLink)}
        </List>
      : <Typography>{t('cards.list.no-cards-registered')}</Typography>
  );
}

export default React.memo(CardsList);
