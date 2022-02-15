import React, { forwardRef } from 'react';
import {
  Link,
  useLocation,
} from 'react-router-dom';

const FolderLink = forwardRef((props, ref) => {
  const { search: urlSearch } = useLocation();
  const { data } = props;
  const path = encodeURIComponent(data?.path);

  // TODO: Introduce fallback incase artist or album are undefined
  const location = `/library/folders/${path}${urlSearch}`;

  return <Link ref={ref} to={location} {...props} />
});

export default FolderLink;
