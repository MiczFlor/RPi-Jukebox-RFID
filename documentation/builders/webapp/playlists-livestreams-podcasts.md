# Playlists, Livestreams and Podcasts

By default, the Phoniebox represents music based on its metadata like album name, artist or song name. The hierarchy and order of songs is determined by their original definition. If you prefer a specific list of songs to be played, you can use playlists (files ending with `*.m3u`). Phoniebox also supports livestreams and podcasts (if connected to the internet) through playlists.

## Playlists
If you like the Phoniebox to play songs in the pre-defined order, you can use `m3u` playlists.

An .m3u playlist is a plain text file that contains a list of file paths or URLs to multimedia files. Each entry in the playlist represents a single song, and they are listed in the order in which they should be played.

### Structure of an .m3u playlist
An .m3u playlist is a simple text document with each song file listed on a separate line. Each entry is optionally preceded by a comment line that starts with a '#' symbol. The actual file paths or URLs of the media files come after the comment.

### Creating an .m3u playlist

1. You can create an .m3u playlist using a plain text editor.
2. Open a new text file
3. [Optional] Start by adding a comment line to provide a description or notes about the playlist.
4. On the following lines, list the file paths or URLs of the media files you want to include in the playlist, one per line. They must refer to true files paths on your Phoniebox. They can be relative or absolute paths.
5. Save the file with the .m3u extension (e.g., my_playlist.m3u).

```
#EXTM3U
Simone Sommerland/Die 30 besten Kindergartenlieder/08 - Pitsch, patsch, Pinguin.mp3
Simone Sommerland/Die 30 besten Spiel- Und Bewegungslieder/12 - Das rote Pferd.mp3
Bibi und Tina/bibi-tina-jetzt-in-echt-kinofilm-soundtrack/bibi-tina-jetzt-in-echt-kinofilm-soundtrack-7-ordinary-girl.mp3
```

### Using .m3u playlist in Phoniebox

The Phoniebox Web App handles the playlists in a way that it allows you to browse its content just like other songs. This means, you won't see the m3u playlist itself and instead, the individual items of the playlist. They also become actionable and you can select individual songs from it to play, or play the entire playlist.

> [!NOTE]
> Files ending with `.m3u` are treated as folder playlist. Regular folder processing is suspended and the playlist is build solely from the `.m3u` content. Only the alphabetically first `.m3u` is processed, others are ignored.

Based on the note above, we suggest to use m3u playlists like this, especially if you like to manage multiple playlists.

1. In the `audiofolder` directory (or any sub-directory), create a new folder.
2. In this new folder, copy your .m3u playlist. Make sure the links to the respective songs are correct.
3. Open the Web App. Under Library, select the Folder view and browse to the new folder you created.
4. You should now be able to browse and play the content of the playlist.

### Assiging a .m3u playlist to a card

In the Phoniebox Web App, .m3u playlists do not show up as individual files. In order to assign a playlist to a card, do the following:

1. [Follow the steps above](#using-m3u-playlist-in-phoniebox) to add a playlist to your Phoniebox (make sure you have created individual folders)
2. In the Web App, open Cards tab and click the "+" button to add a new card
3. As a Jukebox action, select "Play music", then select "Select music"
4. Next (in your your Library view), select the Folder view in the top right corner.
5. Browse to the folder you created (representing your playlist) and click on it.

You are essentially assigning a folder (just like any other conventional folder) to your card representing the content of your playlist.

## Livestreams


## Podcasts