const encodeMessage = (obj) => {
  const payload = JSON.stringify(obj);
  // console.log('encodeMessage', payload);
  return payload;
}

const decodeMessage = (msg) => {
  const { result } = JSON.parse(new TextDecoder().decode(msg));
  console.log('decodeMessage', result);
  return result;
}

export {
  decodeMessage,
  encodeMessage,
}
