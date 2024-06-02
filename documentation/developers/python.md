# Python Development Notes

## Prerequisites

> [!NOTE]
> All Python scripts must be run within a [virtual environment](https://docs.python.org/3/library/venv.html) (`.venv`). All Python plugins are installed encapsulated within this environment.

Before you can run Python code, you need to enable the virtual environment. On the Raspberry Pi, it's located in the project root `~/RPi-Jukebox-RFID/.venv`. Depending on your setup, the absolute path can vary.

```bash
$ source ~/RPi-Jukebox-RFID/.venv/bin/activate
```

If the virtual environment has been activated correctly, your terminal will now show a prefix (`.venv`). If you want to leave the venv again execute deactivate.

```bash
$ deactivate
```
