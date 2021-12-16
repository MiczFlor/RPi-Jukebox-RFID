import React, { useEffect, useState } from "react";
import { useParams } from 'react-router-dom';

import {
  CircularProgress,
  Typography,
} from "@mui/material";

import request from '../../../../utils/request';
import FolderList from "./folder-list";

const Folders = ({
  musicFilter,
  isSelecting,
  registerMusicToCard,
}) => {
  const { dir = './' } = useParams();
  const [folders, setFolders] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const search = ({ name }) => {
    if (musicFilter === '') return true;

    const lowerCaseMusicFilter = musicFilter.toLowerCase();

    return name.toLowerCase().includes(lowerCaseMusicFilter);
  };

  useEffect(() => {
    const fetchFolderList = async () => {
      setIsLoading(true);
      const { result, error } = await request(
        'folderList',
        { folder: decodeURIComponent(dir) }
      );
      setIsLoading(false);

      if(result) setFolders(result);
      if(error) setError(error);
    }

    fetchFolderList();
  }, [dir]);

  const filteredFolders = folders.filter(search);

  if (isLoading) return <CircularProgress />;
  if (error) return <Typography>An error occurred while loading the library.</Typography>;
  if (!filteredFolders.length) {
    if (musicFilter) return <Typography>☝️ No music found!</Typography>;
    return <Typography>This folder is empty! 🙈</Typography>;
  }

  return (
    <FolderList
      dir={dir}
      folders={filteredFolders}
      isSelecting={isSelecting}
      registerMusicToCard={registerMusicToCard}
    />
  );
};

export default Folders;
