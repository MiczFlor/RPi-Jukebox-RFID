import { forwardRef, memo } from 'react';
import { Link } from 'react-router-dom';
import { isNil, reject } from 'ramda';
import { useTranslation } from 'react-i18next';

import {
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemText,
  Typography
} from '@mui/material';

import BookmarkIcon from '@mui/icons-material/Bookmark';

const CardsList = ({ cardsList }) => {
  const { t } = useTranslation();

  const ListItemLink = (cardId) => {
    const card = cardsList[cardId];
    const EditCardLink = forwardRef((props, ref) => {
      return (
        <Link
          ref={ref}
          state={{ id: cardId, ...card }}
          to={`/cards/${cardId}/edit`}
          {...props}
        />
      );
    });
    EditCardLink.displayName = 'EditCardLink';

    const description = card.from_alias
      ? reject(
          isNil,
          [card.from_alias, card.action.args]
        ).join(', ')
      : card.func

    return (
      <ListItem disablePadding key={cardId}>
        <ListItemButton component={EditCardLink} nativeButton={false}>
          <ListItemAvatar>
            <Avatar>
              <BookmarkIcon />
            </Avatar>
          </ListItemAvatar>
          <ListItemText
            primary={cardId}
            secondary={description}
          />
        </ListItemButton>
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

export default memo(CardsList);
