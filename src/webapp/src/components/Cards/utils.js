import {
  isEmpty,
  has,
} from 'ramda';

import commands from '../../commands';
import { JUKEBOX_ACTIONS_MAP } from '../../config';

const mapValuesToKeys = (command, args) => {
  const argKeys = getCommandArgKeys(command);
  const values = argKeys.reduce((prev, arg, pos) => (
    {
      ...prev,
      [arg]: args[pos],
    }
    ), {});

  return values;
};

const getActionAndCommand = (actionData) => {
  const { action, command: { name } = {} } = actionData;

  return { action, command: name };
}

const findActionByCommand = (command) => {
  const action = Object.keys(JUKEBOX_ACTIONS_MAP).find((action) => {
    return has(command)(JUKEBOX_ACTIONS_MAP[action].commands)
  });

  return action;
};

const getCommandArgKeys = (command) => {
  const { [command] : { argKeys = [] } = {} } = commands;

  return argKeys;
};

const buildActionData = (action, command = {}, args = {}) => {
  const data = {
    action,
    command,
  };

  if (!isEmpty(command)) {
    const _args = Array.isArray(args)
      ? mapValuesToKeys(command, args)
      : args;

    data.command = {
      name: command,
      args: _args,
    }
  }

  return data;
};

const getArgsValues = (actionData) => {
  const { command } = getActionAndCommand(actionData);
  const argKeys = getCommandArgKeys(command);

  return argKeys.map(
    key => actionData.command.args[key]
  );
};

export {
  buildActionData,
  findActionByCommand,
  getActionAndCommand,
  getArgsValues,
};
