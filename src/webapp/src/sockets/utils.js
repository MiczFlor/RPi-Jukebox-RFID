const encodeMessage = (obj) => {
  // console.log('encodeMessage', obj);
  const payload = JSON.stringify(obj);
  return payload;
}

const decodeMessage = (msg) => {
  const { result } = JSON.parse(new TextDecoder().decode(msg));
  console.log('decodeMessage', result);
  return result;
}

const decodePubSubMessage = (msg) => {
  const message = new TextDecoder().decode(msg);
  // Message comes like this string
  // 'topicName { "topic": "topicName", ...kwargs }'
  // the below line removes 'topicName ' from the string
  const [topic, data] = message.split(/ (.+)/);
  // The we have pure JSON as string which can be parsed
  const payload = JSON.parse(data);
  // console.log('decodeMessage', result);
  return { topic, [topic]: payload };
}

const preparePayload = (plugin, method, kwargs = {}) => {
  return {
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
