import React, { forwardRef } from 'react';
import { Link } from 'react-router-dom';

const FolderLink = forwardRef((props, ref) => {
  const { data } = props;
  const dir = encodeURIComponent(data?.dir);

  // TODO: Introduce fallback incase artist or album are undefined
  const location = `/library/folders/${dir}`;

  return <Link ref={ref} to={location} {...props} />
});

export default FolderLink;
