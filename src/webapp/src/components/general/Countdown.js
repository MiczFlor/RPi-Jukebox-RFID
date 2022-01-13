import { useEffect, useRef,  useState } from 'react';

import { toHHMMSS } from '../../utils/utils';

const Countdown = ({ onEnd, seconds, stringEnded = undefined }) => {
  // This is required to avoid async updates on unmounted compomemts
  // https://github.com/facebook/react/issues/14227
  const isMounted = useRef(null);

  const [time, setTime] = useState(seconds);

  useEffect(() => {
    isMounted.current = true;

    if (time === 0) return onEnd();
    setTimeout(() => {
      if (isMounted.current) setTime(time - 1)
    }, 1000);

    return () => {
      isMounted.current = false;
    }
  }, [time]);

  if (time) return toHHMMSS(time);
  if (stringEnded) return stringEnded;
  return toHHMMSS(0);
}

export default Countdown;
