import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';

import request from '../../utils/request';
import { JUKEBOX_ACTIONS_MAP } from '../../config';
import CardsForm from './form';

const CardsEdit = () => {
  const { cardId } = useParams();

  const [selectedAction, setSelectedAction] = useState(undefined);
  const [actionData, setActionData] = useState({});

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

  return (
    <CardsForm
      title="Edit card"
      cardId={cardId}
      selectedAction={selectedAction}
      setSelectedAction={setSelectedAction}
      actionData={actionData}
      setActionData={setActionData}
    />
  );
};

export default CardsEdit;
