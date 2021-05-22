const encodeMessage = (obj) => {
  return JSON.stringify(obj);
}

const decodeMessage = (msg) => {
  const { resp } = JSON.parse(new TextDecoder().decode(msg));
  console.log('decodeMessage', resp);

  return resp;
}

export {
  decodeMessage,
  encodeMessage,
}
