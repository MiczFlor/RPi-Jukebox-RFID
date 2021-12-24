import React from 'react';

import CommandSelector from '../../command-selector';

const SelectHost = ({
  actionData,
  handleActionDataChange,
}) => {
  return (
    <CommandSelector
      actionData={actionData}
      handleActionDataChange={handleActionDataChange}
    />
  );
};

export default SelectHost;
