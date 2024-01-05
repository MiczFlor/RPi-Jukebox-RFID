# Spotify Integration

The Spotify integration allows to play music directly from Spotify.

> [!IMPORTANT]
> You need a Spotify Premium subscription to use this functionality

## Needed credentials

For the spotifyd daemon, you need to provide username and password of your Spotify account
during installation. This is used to enable the Phoniebox to play music from Spotify.

To control the playback (spotipy), you need to create an app as Spotify developer and provide the
`client_id` and `client_secret` therefore follow the steps:

1. Access [Developers Dashboard](https://developer.spotify.com/dashboard)
2. Create an App via the button on the top right
3. Fill in following fields:
    - App name: `your_desired_name`
    - Redirect URI: `http://localhost:3001`
4. Save the `client_id` and `client_secret` for the installation

## Post installation configuration
### spotifyd

The spotifyd daemon is using the username and password of your Spotify account.

If the credentials changed, you can update them in the config file located at `/etc/spotifyd.conf`

### spotipy

Spotipy is using `client_id` and `client_secret` to controll the playback of the Phoniebox.

To update the credentials, please modify the file located at `~/RPi-Jukebox-RFID/shared/settings/player.yaml`

## Resources

- [spotifyd](https://spotifyd.rs/)
- [spotipy](https://spotipy.readthedocs.io)
