import {
  createUploadSelection,
  uploadSelectionFromDataTransfer,
} from './upload-selection';

const fileEntry = (file) => ({
  isDirectory: false,
  isFile: true,
  name: file.name,
  file: (resolve) => resolve(file),
});

const directoryEntry = (name, children) => ({
  isDirectory: true,
  isFile: false,
  name,
  createReader: () => {
    let read = false;
    return {
      readEntries: (resolve) => {
        resolve(read ? [] : children);
        read = true;
      },
    };
  },
});

test('derives complete folder trees from directory picker paths', () => {
  const first = new File(['one'], 'one.mp3');
  const second = new File(['two'], 'two.mp3');
  Object.defineProperty(first, 'webkitRelativePath', {
    value: 'First Album/Disc 1/one.mp3',
  });
  Object.defineProperty(second, 'webkitRelativePath', {
    value: 'Second Album/two.mp3',
  });

  expect(createUploadSelection([first, second])).toEqual({
    files: [
      { file: first, relativePath: 'First Album/Disc 1/one.mp3' },
      { file: second, relativePath: 'Second Album/two.mp3' },
    ],
    folders: ['First Album', 'Second Album', 'First Album/Disc 1'],
  });
});

test('recursively reads multiple dropped folders and retains empty folders', async () => {
  const first = new File(['one'], 'one.mp3');
  const second = new File(['two'], 'two.mp3');
  const firstAlbum = directoryEntry('First Album', [
    directoryEntry('Disc 1', [fileEntry(first)]),
    directoryEntry('Empty', []),
  ]);
  const secondAlbum = directoryEntry('Second Album', [fileEntry(second)]);

  await expect(uploadSelectionFromDataTransfer({
    items: [
      { webkitGetAsEntry: () => firstAlbum },
      { webkitGetAsEntry: () => secondAlbum },
    ],
  })).resolves.toEqual({
    files: [
      { file: first, relativePath: 'First Album/Disc 1/one.mp3' },
      { file: second, relativePath: 'Second Album/two.mp3' },
    ],
    folders: [
      'First Album',
      'Second Album',
      'First Album/Disc 1',
      'First Album/Empty',
    ],
  });
});
