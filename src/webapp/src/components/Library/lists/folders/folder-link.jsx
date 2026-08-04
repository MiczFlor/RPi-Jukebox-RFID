import { forwardRef } from 'react';
import {
  Link,
  useLocation,
  useParams,
} from 'react-router-dom';

const FolderLink = forwardRef((props, ref) => {
  const { search: urlSearch } = useLocation();
  const {
    provider = 'mpd',
    view = 'folders',
  } = useParams();
  const { data, ...linkProps } = props;
  const dir = encodeURIComponent(data?.dir);

  // TODO: Introduce fallback incase artist or album are undefined
  const location = `/library/${provider}/${view}/${dir}${urlSearch}`;

  return <Link ref={ref} to={location} {...linkProps} />
});
FolderLink.displayName = 'FolderLink';

export default FolderLink;
