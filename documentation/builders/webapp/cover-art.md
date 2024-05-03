# Cover Art

## Enable/Disable Cover Art

The Web App automatically searches for cover art for albums and songs. If it finds cover art, it displays it; if not, it shows a placeholder image. However, you may prefer to disable cover art (e.g. in situations where device performance is low; screen space is limited; etc). There are two ways to do this:

1. **Web App Settings**: Go to the "Settings" tab. Under the "General" section, find and toggle the "Show Cover Art" option.
1. **Configuration File**: Open the `jukebox.yaml` file. Navigate to `webapp` -> `show_covers`. Set this value to `true` to enable or `false` to disable cover art display. If this option does not exist, it assumes `true` as a default.

## Providing Additional Cover Art

Cover art can be provided in two ways: 1) embedded within the audio file itself, or 2) as a separate image file in the same directory as the audio file. The software searches for cover art in the order listed.

To add cover art using the file system, place a file named `cover.jpg` in the same folder as your audio file or album. Accepted image file types are `jpg` and `png`.

### Example

Suppose none of your files currently include embedded cover art, the example below demonstrates how to enable cover art for an entire folder, applying the same cover art to all files within that folder.

> [!IMPORTANT]
> You cannot assign different cover arts to different tracks within the same folder.

#### Example Folder Structure

```text
└── audiofolders
    ├── Simone Sommerland
    │   ├── 01 Aramsamsam.mp3
    │   ├── 02 Das Rote Pferd.mp3
    │   ├── 03 Hoch am Himmel.mp3
    │   └── cover.jpg               <- Cover Art file as JPG
    └── Bibi und Tina
        ├── 01 Bibi und Tina Song.mp3
        ├── 02 Alles geht.mp3
        ├── 03 Solange dein Herz spricht.mp3
        └── cover.png               <- Cover Art file as PNG
```
