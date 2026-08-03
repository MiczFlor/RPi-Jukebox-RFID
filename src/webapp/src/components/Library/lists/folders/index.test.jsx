import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  test,
  vi,
} from 'vitest';

import {
  deleteLibraryEntries,
  listLibraryEntries,
  refreshLibrary,
  uploadLibraryFile,
} from '../../../../utils/library-api';
import Folders from './index';

vi.mock('../../../../utils/library-api', () => ({
  ACCEPTED_LIBRARY_FILES: '.mp3,.txt',
  createLibraryFolder: vi.fn(),
  deleteLibraryEntries: vi.fn(),
  listLibraryEntries: vi.fn(),
  refreshLibrary: vi.fn(),
  translateLibraryError: (t, error) => error.message,
  uploadLibraryFile: vi.fn(),
}));
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key, options = {}) => {
      const labels = {
        'general.buttons.cancel': 'Cancel',
        'general.buttons.close': 'Close',
        'general.buttons.delete': 'Delete',
        'library.folders.empty-folder': 'This folder is empty',
        'library.folders.manager.actions-label': 'Library file actions',
        'library.folders.manager.create-folder': 'New folder',
        'library.folders.manager.delete-selected': `Delete ${options.count} items`,
        'library.folders.manager.delete.permanent': 'Deletion is permanent.',
        'library.folders.manager.delete.folder-warning': 'Folder contents will be deleted.',
        'library.folders.manager.delete.title': `Delete ${options.count} items?`,
        'library.folders.manager.drop-files': 'Drop files here.',
        'library.folders.manager.select': 'Select',
        'library.folders.manager.select-item': `Select ${options.name}`,
        'library.folders.manager.upload': 'Upload',
        'library.folders.manager.upload-files': 'Upload files',
        'library.folders.manager.upload-folders': 'Upload folders',
        'library.folders.manager.upload-dialog.cancel-all': 'Cancel all',
        'library.folders.manager.upload-dialog.cancel-item': 'Cancel',
        'library.folders.manager.upload-dialog.progress': `Progress ${options.name}`,
        'library.folders.manager.upload-dialog.retry-item': 'Retry',
        'library.folders.manager.upload-dialog.status.complete': 'Uploaded',
        'library.folders.manager.upload-dialog.status.queued': 'Waiting',
        'library.folders.manager.upload-dialog.title': 'Upload files and folders',
        'library.folders.manager.upload-dialog.uploading': `Uploading ${options.progress}%`,
        'library.folders.show-folder-content': 'Show folder content',
      };
      return labels[key] || key;
    },
  }),
}));

const entries = [
  {
    name: 'Album',
    relpath: 'Album',
    type: 'directory',
  },
  {
    name: 'track.mp3',
    relpath: 'track.mp3',
    type: 'file',
  },
];

const renderFolders = () => render(
  <MemoryRouter initialEntries={['/library/folders/.']}>
    <Routes>
      <Route
        path="/library/folders/:dir"
        element={
          <Folders
            isSelecting={false}
            musicFilter=""
            registerMusicToCard={vi.fn()}
          />
        }
      />
    </Routes>
  </MemoryRouter>,
);

describe('responsive library file management', () => {
  beforeEach(() => {
    listLibraryEntries.mockResolvedValue(entries);
    deleteLibraryEntries.mockResolvedValue({ deleted: ['Album'] });
    refreshLibrary.mockResolvedValue({ update_id: '1' });
    uploadLibraryFile.mockResolvedValue({ path: 'track.mp3', size: 5 });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  test('provides visible touch/click controls and confirms batch deletion', async () => {
    const user = userEvent.setup();
    renderFolders();

    expect(await screen.findByRole('toolbar', { name: 'Library file actions' })).toBeVisible();
    await user.click(screen.getByRole('button', { name: 'Upload' }));
    expect(screen.getByRole('menuitem', { name: 'Upload files' })).toBeVisible();
    expect(screen.getByRole('menuitem', { name: 'Upload folders' })).toBeVisible();
    await user.keyboard('{Escape}');
    const fileInputs = Array.from(document.querySelectorAll('input[type="file"]'));
    expect(fileInputs).toHaveLength(2);
    const folderInput = fileInputs.find((input) => input.hasAttribute('webkitdirectory'));
    expect(folderInput).toHaveAttribute('multiple');
    expect(folderInput).toHaveAttribute('webkitdirectory');
    expect(screen.getByRole('button', { name: 'New folder' })).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Delete Album' })).not.toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Select' }));
    await user.click(screen.getByRole('checkbox', { name: 'Select Album' }));
    await user.click(screen.getByRole('button', { name: 'Delete 1 items' }));

    expect(screen.getByText('Deletion is permanent.')).toBeVisible();
    expect(screen.getByText('Folder contents will be deleted.')).toBeVisible();
    const deleteDialog = screen.getByRole('dialog', { name: 'Delete 1 items?' });
    expect(within(deleteDialog).getAllByText('Album')).toHaveLength(1);
    await act(async () => {
      await user.click(screen.getByRole('button', { name: 'Delete' }));
      await Promise.resolve();
      await Promise.resolve();
    });

    await waitFor(() => {
      expect(deleteLibraryEntries).toHaveBeenCalledWith(['Album']);
      expect(refreshLibrary).toHaveBeenCalled();
    });
    await waitFor(() => {
      expect(screen.queryByText('Deletion is permanent.')).not.toBeInTheDocument();
      expect(listLibraryEntries).toHaveBeenCalledTimes(2);
    });
  });

  test('supports drag and drop uploads and refreshes the library after the batch', async () => {
    const { container } = renderFolders();
    await screen.findByRole('toolbar', { name: 'Library file actions' });
    const dropTarget = container.firstChild;
    const file = new File(['audio'], 'new track.mp3', { type: 'audio/mpeg' });

    await act(async () => {
      fireEvent.drop(dropTarget, {
        dataTransfer: { files: [file] },
      });
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(await screen.findByRole('dialog', { name: 'Upload files and folders' })).toBeVisible();
    await waitFor(() => expect(uploadLibraryFile).toHaveBeenCalledWith(
      expect.objectContaining({
        file,
        folder: '.',
      }),
    ));
    await waitFor(() => expect(refreshLibrary).toHaveBeenCalled());
    expect(await screen.findByText('Uploaded')).toBeVisible();
    await waitFor(() => expect(listLibraryEntries).toHaveBeenCalledTimes(2));
  });
});
