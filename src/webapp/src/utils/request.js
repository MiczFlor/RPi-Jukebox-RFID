import { socketRequest } from "../sockets";
import commands from "../commands";

const request = async (command, kwargs = {}) => {
  try {
    if (!(command in commands)) {
      throw new Error(`'${command}' does not exist in command object`);
    }

    const { _package, plugin, method = null } = commands[command];

    // Send request
    const result = await socketRequest(_package, plugin, method, kwargs);
    return { result };
  }
  catch (error) {
    console.error(`${command}: `, error);
    return { error };
  };
};

export default request;
