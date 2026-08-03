import { useEffect, useState } from 'react';

import { toHHMMSS } from '../../utils/utils';

const normalizeSeconds = (seconds) => (
  Math.max(0, Number(seconds) || 0)
);

const Countdown = ({ resetKey, seconds, stringEnded = undefined }) => {
  const [time, setTime] = useState(() => normalizeSeconds(seconds));

  useEffect(() => {
    const initialSeconds = normalizeSeconds(seconds);
    const deadline = Date.now() + initialSeconds * 1000;
    setTime(initialSeconds);

    if (initialSeconds === 0) {
      return undefined;
    }

    const interval = setInterval(() => {
      setTime(Math.max(0, (deadline - Date.now()) / 1000));
    }, 250);
    return () => clearInterval(interval);
  }, [resetKey, seconds]);

  if (time) return toHHMMSS(Math.round(time));
  if (stringEnded) return stringEnded;
  return toHHMMSS(0);
}

export default Countdown;
