# Playlists, Livestreams and Podcasts

By default, the Phoniebox represents music based on its metadata like album name, artist or song name. The hierarchy and order of songs is determined by their original definition. If you prefer a specific list of songs to be played, you can use playlists (files ending with `*.m3u`). Phoniebox also supports livestreams and podcasts (if connected to the internet) through playlists.

## Playlists
If you like the Phoniebox to play songs in the pre-defined order, you can use .m3u playlists.

An .m3u playlist is a plain text file that contains a list of file paths or URLs to multimedia files. Each entry in the playlist represents a single song, and they are listed in the order in which they should be played.

### Structure of an .m3u playlist
An .m3u playlist is a simple text document with each song file listed on a separate line. Each entry is optionally preceded by a comment line that starts with a '#' symbol. The actual file paths or URLs of the media files come after the comment.

### Creating an .m3u playlist

1. You can create an .m3u playlist using a plain text editor.
2. Open a new text file
3. [Optional] Start by adding a comment line to provide a description or notes about the playlist.
4. On the following lines, list the file paths or URLs of the media files you want to include in the playlist, one per line. They must refer to true files paths on your Phoniebox. They can be relative or absolute paths.
5. Save the file with the .m3u extensionm, e.g. `my_playlist.m3u`.

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

1. In the `audiofolders` directory (or any sub-directory), create a new folder.
2. In this new folder, copy your .m3u playlist. Make sure the links to the respective songs are correct.
3. Open the Web App. Under Library, select the Folder view and browse to the new folder you created.
4. You should now be able to browse and play the content of the playlist.

#### Example folder structure

```
* audiofolders
  * wake-up-songs
    playlist.m3u
  * lullabies-sleep-well
    playlist.m3u
```

### Assigning a .m3u playlist to a card

In the Phoniebox Web App, .m3u playlists do not show up as individual files. In order to assign a playlist to a card, do the following:

1. [Follow the steps above](#using-m3u-playlist-in-phoniebox) to add a playlist to your Phoniebox (make sure you have created individual folders).
2. In the Web App, open Cards tab and click the "+" button to add a new card.
3. As a Jukebox action, select "Play music", then select "Select music".
4. Next (in your your Library view), select the Folder view in the top right corner.
5. Browse to the folder you created (representing your playlist) and click on it.

You are essentially assigning a folder (just like any other conventional folder) to your card representing the content of your playlist.

## Livestreams

In order to play radio livestreams on your Phoniebox, you use playlists to register your livestream and make it accessible.

### Using livestream.txt playlist in Phoniebox

1. [Follow the steps above](#using-m3u-playlist-in-phoniebox) to add a playlist to your Phoniebox (make sure you have created individual folders).
2. When creating the playlist file, make sure it call or at least ends with `livestream.txt` instead of `*.m3u` (Examples: `awesome-livestream.txt`, `livestream.txt`).
3. Add links to your livestreams just like you would with songs in .m3u playlists

You can now assign livestreams to cards [following the example](#assiging-a-m3u-playlist-to-a-card) of playlists.

#### Example folder structure and playlist names

```
* audiofolders
  * wdr-kids
    wdr-kids-livestream.txt
  * energy
    cool-livestream.txt
  * classic
    livestream.txt
```

#### Example of livestream.txt

```txt
https://wdr-diemaus-live.icecastssl.wdr.de/wdr/diemaus/live/mp3/128/stream.mp3
http://channels.webradio.antenne.de/hits-fuer-kids
```

## Podcasts

Just like you add livestreams to the Phoniebox, you can also add individual Podcasts or entire Podcast feeds to the Phoniebox.

You have 3 options to play Podcasts

1. Create a playlist and reference individual direct links to Podcast episodes (just like livestreams)
2. Provide a Podcast RSS feed
3. Download the MP3 and add them like normal songs to your Phoniebox. This makes them available offline.

We will explain options 1 and 2 more closely.

### Using podcast.txt playlist in Phoniebox

1. [Follow the steps above](#using-m3u-playlist-in-phoniebox) to add a playlist to your Phoniebox (make sure you have created individual folders).
2. When creating the playlist file, make sure it ends with `podcasts.txt` instead of `*.m3u`. (Examples: `awesome-podcast.txt`, `podcast.txt`).
3. Add links to your individual podcast episodes just like you would with songs in .m3u playlists
4. As an alternative, you can provide a single RSS feed (XML). Phoniebox will expand the file and refer to all episodes listed within this file.

#### Example folder structure and playlist names

```
* audiofolders
  * die-maus
    die-maus-podcast.txt
  * miras-welt
    cool-podcast.txt
  * kakadu
    podcast.txt
```

#### Example of podcast.txt for individual episodes

```txt
https://podcastb11277.podigee.io/94-ich-ware-gerne-beliebt-wie-geht-das
https://podcastb11277.podigee.io/91-wieso-kann-ich-nicht-den-ganzen-tag-fernsehen
```

#### Example of podcast.txt for RSS feeds (XML)

```txt
https://kinder.wdr.de/radio/diemaus/audio/diemaus-60/diemaus-60-106.podcast
```

```txt
http://www.kakadu.de/podcast-kakadu.2730.de.podcast.xml
```
