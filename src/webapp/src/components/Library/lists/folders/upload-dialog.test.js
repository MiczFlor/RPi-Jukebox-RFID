import React from 'react';
import {
  act,
  render,
  screen,
  waitFor,
} from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import {
  refreshLibrary,
  uploadLibraryFile,
} from '../../../../utils/library-api';
import UploadDialog from './upload-dialog';

jest.mock('../../../../utils/library-api', () => ({
  refreshLibrary: jest.fn(),
  translateLibraryError: (t, error) => error.message,
  uploadLibraryFile: jest.fn(),
}));
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key, options = {}) => {
      const labels = {
        'general.buttons.close': 'Close',
        'library.folders.manager.upload-dialog.cancel-all': 'Cancel all',
        'library.folders.manager.upload-dialog.cancel-file': 'Cancel upload',
        'library.folders.manager.upload-dialog.progress': `Progress ${options.name}`,
        'library.folders.manager.upload-dialog.retry-file': 'Retry upload',
        'library.folders.manager.upload-dialog.status.cancelled': 'Cancelled',
        'library.folders.manager.upload-dialog.status.complete': 'Uploaded',
        'library.folders.manager.upload-dialog.status.queued': 'Waiting',
        'library.folders.manager.upload-dialog.title': 'Upload files',
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
      files={[first, second]}
      folder="Album"
      onClose={jest.fn()}
      onLibraryChanged={jest.fn()}
      open
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
    await user.click(screen.getByRole('button', { name: 'Retry upload' }));
    await Promise.resolve();
    await Promise.resolve();
  });
  await waitFor(() => expect(uploadLibraryFile).toHaveBeenCalledTimes(3));
  expect(uploadLibraryFile.mock.calls[2][0].file).toBe(second);
  await waitFor(() => expect(refreshLibrary).toHaveBeenCalled());
});
