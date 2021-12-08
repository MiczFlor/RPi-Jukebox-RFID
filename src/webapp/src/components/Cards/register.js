import React, { useContext, useEffect, useState } from 'react';

import PubSubContext from '../../context/pubsub/context';
import CardsForm from './form';

const CardsRegister = () => {
  const { state } = useContext(PubSubContext);
  const { 'rfid.card_id': swipedCardId } = state;

  const [cardId, setCardId] = useState(
    swipedCardId
    || undefined
    // || "9123134298459334" // For testing purposes only
  );

  const [selectedAction, setSelectedAction] = useState(undefined);
  const [actionData, setActionData] = useState({});

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
