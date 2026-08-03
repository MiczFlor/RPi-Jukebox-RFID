import {
  act,
  render,
  screen,
  waitFor,
} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  beforeEach,
  expect,
  test,
  vi,
} from 'vitest';

import {
  createLibraryFolder,
  refreshLibrary,
  uploadLibraryFile,
} from '../../../../utils/library-api';
import UploadDialog from './upload-dialog';

vi.mock('../../../../utils/library-api', () => ({
  createLibraryFolder: vi.fn(),
  refreshLibrary: vi.fn(),
  translateLibraryError: (t, error) => error.message,
  uploadLibraryFile: vi.fn(),
}));
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key, options = {}) => {
      const labels = {
        'general.buttons.close': 'Close',
        'library.folders.manager.upload-dialog.cancel-all': 'Cancel all',
        'library.folders.manager.upload-dialog.cancel-item': 'Cancel',
        'library.folders.manager.upload-dialog.creating-folder': 'Creating folder',
        'library.folders.manager.upload-dialog.folder-created': 'Folder created',
        'library.folders.manager.upload-dialog.parent-folder-failed': 'Parent folder failed',
        'library.folders.manager.upload-dialog.progress': `Progress ${options.name}`,
        'library.folders.manager.upload-dialog.retry-item': 'Retry',
        'library.folders.manager.upload-dialog.status.cancelled': 'Cancelled',
        'library.folders.manager.upload-dialog.status.complete': 'Uploaded',
        'library.folders.manager.upload-dialog.status.queued': 'Waiting',
        'library.folders.manager.upload-dialog.title': 'Upload files and folders',
        'library.folders.manager.upload-dialog.uploading': `Uploading ${options.progress}%`,
      };
      return labels[key] || key;
    },
  }),
}));

const deferred = () => {
  let resolve;
  let reject;
  const promise = new Promise((promiseResolve, promiseReject) => {
    resolve = promiseResolve;
    reject = promiseReject;
  });
  return { promise, reject, resolve };
};

beforeEach(() => {
  vi.clearAllMocks();
});

test('uploads sequentially and retries failed files', async () => {
  const firstUpload = deferred();
  uploadLibraryFile
    .mockReturnValueOnce(firstUpload.promise)
    .mockRejectedValueOnce(new Error('Storage failed.'))
    .mockResolvedValueOnce({ path: 'second.mp3' });
  refreshLibrary.mockResolvedValue({ update_id: '1' });
  const first = new File(['first'], 'first.mp3');
  const second = new File(['second'], 'second.mp3');

  render(
    <UploadDialog
      folder="Album"
      onClose={vi.fn()}
      onLibraryChanged={vi.fn()}
      open
      selection={{
        files: [
          { file: first, relativePath: first.name },
          { file: second, relativePath: second.name },
        ],
        folders: [],
      }}
    />,
  );

  await waitFor(() => expect(uploadLibraryFile).toHaveBeenCalledTimes(1));
  expect(uploadLibraryFile.mock.calls[0][0].file).toBe(first);

  await act(async () => {
    firstUpload.resolve({ path: 'Album/first.mp3' });
    await firstUpload.promise;
    await Promise.resolve();
    await Promise.resolve();
  });

  await waitFor(() => expect(uploadLibraryFile).toHaveBeenCalledTimes(2));
  expect(uploadLibraryFile.mock.calls[1][0].file).toBe(second);
  expect(await screen.findByText('Storage failed.')).toBeVisible();

  const user = userEvent.setup();
  await act(async () => {
    await user.click(screen.getByRole('button', { name: 'Retry' }));
    await Promise.resolve();
    await Promise.resolve();
  });
  await waitFor(() => expect(uploadLibraryFile).toHaveBeenCalledTimes(3));
  expect(uploadLibraryFile.mock.calls[2][0].file).toBe(second);
  await waitFor(() => expect(refreshLibrary).toHaveBeenCalled());
});

test('creates selected folder trees before uploading their files', async () => {
  createLibraryFolder.mockResolvedValue({});
  uploadLibraryFile.mockResolvedValue({});
  refreshLibrary.mockResolvedValue({ update_id: '1' });
  const file = new File(['audio'], 'track.mp3');

  render(
    <UploadDialog
      folder="Existing"
      onClose={vi.fn()}
      onLibraryChanged={vi.fn()}
      open
      selection={{
        files: [{ file, relativePath: 'Album/Disc 1/track.mp3' }],
        folders: ['Album', 'Album/Disc 1'],
      }}
    />,
  );

  await waitFor(() => expect(uploadLibraryFile).toHaveBeenCalled());
  expect(createLibraryFolder).toHaveBeenNthCalledWith(
    1,
    'Existing',
    'Album',
    expect.objectContaining({ signal: expect.any(AbortSignal) }),
  );
  expect(createLibraryFolder).toHaveBeenNthCalledWith(
    2,
    'Existing/Album',
    'Disc 1',
    expect.objectContaining({ signal: expect.any(AbortSignal) }),
  );
  expect(uploadLibraryFile).toHaveBeenCalledWith(expect.objectContaining({
    file,
    folder: 'Existing/Album/Disc 1',
  }));
  expect(await screen.findAllByText('Folder created')).toHaveLength(2);
  await waitFor(() => expect(refreshLibrary).toHaveBeenCalled());
});

test('does not upload descendants when their parent folder creation fails', async () => {
  createLibraryFolder.mockRejectedValue({
    code: 'duplicate_name',
    message: 'Folder already exists.',
  });
  const file = new File(['audio'], 'track.mp3');

  render(
    <UploadDialog
      folder="."
      onClose={vi.fn()}
      onLibraryChanged={vi.fn()}
      open
      selection={{
        files: [{ file, relativePath: 'Album/track.mp3' }],
        folders: ['Album'],
      }}
    />,
  );

  expect(await screen.findByText('Folder already exists.')).toBeVisible();
  expect(await screen.findByText('Parent folder failed')).toBeVisible();
  expect(uploadLibraryFile).not.toHaveBeenCalled();
});
