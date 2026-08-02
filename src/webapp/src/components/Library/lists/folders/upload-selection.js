const normalizeRelativePath = (path) => String(path || '')
  .replace(/^\/+/, '')
  .split('/')
  .filter(Boolean)
  .join('/');

const addFolderAndParents = (folderPaths, path) => {
  const parts = normalizeRelativePath(path).split('/').filter(Boolean);
  for (let index = 1; index <= parts.length; index += 1) {
    folderPaths.add(parts.slice(0, index).join('/'));
  }
};

const createUploadSelection = (selectedFiles = [], selectedFolders = []) => {
  const files = Array.from(selectedFiles).map((selectedFile) => {
    const file = selectedFile.file || selectedFile;
    return {
      file,
      relativePath: normalizeRelativePath(
        selectedFile.relativePath || file.webkitRelativePath || file.name,
      ),
    };
  });

  const folderPaths = new Set();
  Array.from(selectedFolders).forEach((path) => addFolderAndParents(folderPaths, path));
  files.forEach(({ relativePath }) => {
    const parts = relativePath.split('/');
    parts.pop();
    if (parts.length) addFolderAndParents(folderPaths, parts.join('/'));
  });

  const folders = Array.from(folderPaths).sort((left, right) => {
    const depthDifference = left.split('/').length - right.split('/').length;
    return depthDifference || left.localeCompare(right);
  });
  return { files, folders };
};

const readDirectoryEntries = async (reader) => {
  const entries = [];
  while (true) {
    const batch = await new Promise((resolve, reject) => {
      reader.readEntries(resolve, reject);
    });
    if (!batch.length) return entries;
    entries.push(...batch);
  }
};

const fileFromEntry = (entry) => new Promise((resolve, reject) => {
  entry.file(resolve, reject);
});

const walkEntry = async (entry, parentPath, files, folders) => {
  const relativePath = normalizeRelativePath(
    parentPath ? `${parentPath}/${entry.name}` : entry.name,
  );
  if (entry.isDirectory) {
    folders.push(relativePath);
    const children = await readDirectoryEntries(entry.createReader());
    for (const child of children) {
      await walkEntry(child, relativePath, files, folders);
    }
    return;
  }
  if (entry.isFile) {
    files.push({
      file: await fileFromEntry(entry),
      relativePath,
    });
  }
};

const uploadSelectionFromDataTransfer = async (dataTransfer) => {
  const entries = Array.from(dataTransfer?.items || [])
    .map((item) => item.webkitGetAsEntry?.())
    .filter(Boolean);

  if (!entries.length) {
    return createUploadSelection(dataTransfer?.files || []);
  }

  const files = [];
  const folders = [];
  for (const entry of entries) {
    await walkEntry(entry, '', files, folders);
  }
  return createUploadSelection(files, folders);
};

const uploadSelectionHasEntries = ({ files = [], folders = [] } = {}) => (
  files.length > 0 || folders.length > 0
);

export {
  createUploadSelection,
  uploadSelectionFromDataTransfer,
  uploadSelectionHasEntries,
};
