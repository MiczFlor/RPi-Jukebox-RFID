import { useCallback, useEffect, useRef,  useState } from 'react';

import { toHHMMSS } from '../../utils/utils';

const Counter = ({
  seconds,
  direction = 'down',
  end = 0,
  paused = false,
  onEnd = () => {},
  stringEnded = undefined
}) => {
  // This is required to avoid async updates on unmounted components
  // https://github.com/facebook/react/issues/14227
  const isMounted = useRef(null);
  const [time, setTime] = useState(parseInt(seconds));

  const onEndCallback = useCallback(() => onEnd(), [onEnd]);

  useEffect(() => {
    isMounted.current = true;

    const summand = direction === 'down' ? -1 : 1;

    if (!paused) {
      if (time >= end) return onEndCallback();
      setTimeout(() => {
        if (isMounted.current) setTime(time + summand)
      }, 1000);
    }

    return () => {
      isMounted.current = false;
    }
  }, [
    direction,
    end,
    onEndCallback,
    paused,
    time,
  ]);

  if (time) return toHHMMSS(time);
  if (stringEnded) return stringEnded;
  return toHHMMSS(0);
}

export default Counter;
