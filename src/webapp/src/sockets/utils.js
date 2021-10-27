const encodeMessage = (obj) => {
  // console.log('encodeMessage', obj);
  const payload = JSON.stringify(obj);
  return payload;
}

const decodeMessage = (msg) => {
  const {
    id = undefined,
    error = undefined,
    result = undefined,
  } = JSON.parse(new TextDecoder().decode(msg));

  return { id, result, error };
}

const decodePubSubMessage = (_topic, _payload) => {
  const topic = new TextDecoder().decode(_topic);
  const payload = new TextDecoder().decode(_payload);

  try {
    const data = JSON.parse(payload);

    return { topic, data };
  }
  catch (error) {
    return { topic,  error };
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
