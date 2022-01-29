import React, { useContext, useEffect, useState } from 'react';
import { omit } from 'ramda';
import { useTranslation } from 'react-i18next';

import PubSubContext from '../../context/pubsub/context';
import CardsForm from './form';
import { useLocation } from 'react-router';

const CardsRegister = () => {
  const { t } = useTranslation();
  const {
    state: { 'rfid.card_id': swipedCardId },
    setState
  } = useContext(PubSubContext);
  const { state: locationState } = useLocation();
  const { registerCard } = locationState || {};

  const [cardId, setCardId] = useState(undefined);
  const [actionData, setActionData] = useState(registerCard?.actionData || {});

  useEffect(() => {
    setState(state => (omit(['rfid.card_id'], state)));
  }, [setState]);

  useEffect(() => {
    setCardId(swipedCardId || registerCard?.cardId);
  }, [registerCard, swipedCardId])

  return (
    <CardsForm
      title={t('cards.register.register-card')}
      cardId={cardId}
      actionData={actionData}
      setActionData={setActionData}
    />
  );
};

export default CardsRegister;
