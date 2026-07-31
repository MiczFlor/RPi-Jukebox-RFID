const encodeMessage = (obj) => {
  return JSON.stringify(obj);
}

const decodeMessage = (msg) => {
  const decoded = (typeof msg === 'string') ?
    JSON.parse(msg) :
    msg;
  const {
    id = undefined,
    error = undefined,
    result = undefined,
  } = decoded;

  return { id, result, error };
}

const decodePubSubMessage = (message) => {
  try {
    const decoded = (typeof message === 'string') ?
      JSON.parse(message) :
      message;
    const {
      type,
      topic,
      data = undefined,
    } = decoded;

    if (!['event', 'revoke'].includes(type) || typeof topic !== 'string') {
      throw new Error('Invalid event message.');
    }
    return { type, topic, data };
  }
  catch (error) {
    return { error };
  }
}

const preparePayload = (
  requestId,
  _package,
  plugin,
  method,
  kwargs = {},
) => {
  return {
    id: requestId,
    package: _package,
    plugin,
    method,
    kwargs,
  };
}

export {
  decodeMessage,
  decodePubSubMessage,
  encodeMessage,
  preparePayload,
}
