import React, { useContext, useEffect, useState } from 'react';
import { omit } from 'ramda';

import PubSubContext from '../../context/pubsub/context';
import CardsForm from './form';

const CardsRegister = () => {
  const { state: { 'rfid.card_id': swipedCardId }, setState } = useContext(PubSubContext);

  const [cardId, setCardId] = useState(undefined);
  const [selectedAction, setSelectedAction] = useState(undefined);
  const [actionData, setActionData] = useState({});

  useEffect(() => {
    setState(state => (omit(['rfid.card_id'], state)));
  }, []);

  useEffect(() => {
    setCardId(swipedCardId);
  }, [swipedCardId])

  return (
    <CardsForm
      title="Register a card"
      cardId={cardId}
      selectedAction={selectedAction}
      setSelectedAction={setSelectedAction}
      actionData={actionData}
      setActionData={setActionData}
    />
  );
};

export default CardsRegister;
