import { forwardRef } from 'react';
import {
  Link,
  useLocation,
} from 'react-router-dom';

const FolderLink = forwardRef((props, ref) => {
  const { search: urlSearch } = useLocation();
  const { data, ...linkProps } = props;
  const dir = encodeURIComponent(data?.dir);

  // TODO: Introduce fallback incase artist or album are undefined
  const location = `/library/folders/${dir}${urlSearch}`;

  return <Link ref={ref} to={location} {...linkProps} />
});
FolderLink.displayName = 'FolderLink';

export default FolderLink;
