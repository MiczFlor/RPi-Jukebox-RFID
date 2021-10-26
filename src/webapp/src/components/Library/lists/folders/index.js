import React, { useEffect, useState } from "react";
import { useParams } from 'react-router-dom';

import {
  CircularProgress,
  Typography,
} from "@mui/material";

import request from '../../../../utils/request';
import FolderList from "./folder-list";

const Folders = ({ searchQuery }) => {
  const { dir = './' } = useParams();
  const [folders, setFolders] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const search = ({ name }) => {
    if (searchQuery === '') return true;

    const lowerCaseSearchQuery = searchQuery.toLowerCase();

    return name.toLowerCase().includes(lowerCaseSearchQuery);
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
    if (searchQuery) return <Typography>☝️ No music found!</Typography>;
    return <Typography>This folder is empty! 🙈</Typography>;
  }

  return (
    <FolderList
      folders={filteredFolders}
      dir={dir}
    />
  );
};

export default Folders;
