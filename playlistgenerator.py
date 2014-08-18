# Created by Rob Ruenes <robruenes@gmail.com> on 8/14/2014
# For use with RedditRocks

import spotify
import threading
import getpass

"""
Helper class, searches Spotify for tracks and builds playlists
"""

class SpotifyPlaylistGenerator(object):

  def __init__(self):
    self._session = spotify.Session()
    self._spotify_tracks = []
    self._tracks_added_event = threading.Event()
    self._playlist_updated_event = threading.Event()

  def _tracks_added(self, playlist, tracks, index):
    self._tracks_added_event.set()

  def _updating_playlist(self, playlist, done):
    if done is True:
      self._playlist_updated_event.set()

  def _generate_playlist(self, playlist_name):

    """Reset the events for each subsequent call to this function, so we don't
       accidentally quit before a playlist is fully updated"""

    self._tracks_added_event.clear()
    self._playlist_updated_event.clear()

    playlist = self._session.playlist_container.add_new_playlist(playlist_name)
    playlist.on(spotify.PlaylistEvent.TRACKS_ADDED, self._tracks_added)
    playlist.on(spotify.PlaylistEvent.PLAYLIST_UPDATE_IN_PROGRESS, self._updating_playlist)

    print 'Building playlist %s with discovered tracks...' % playlist_name
    playlist.add_tracks(self._spotify_tracks)
    playlist.load()

    while not self._tracks_added_event.wait(0.1):
      self._session.process_events()

    while not self._playlist_updated_event.wait(0.1):
      self._session.process_events()

    print "Playlist built!\n"

  def _perform_search(self, queries):
    result = None

    for query in queries:

      search = spotify.Search(self._session, query)

      while not search.is_loaded:
          search.load()

      if search.track_total < 1:
        continue

      result = search
      break

    return result


  def _search_for_tracks(self, desired_tracks):

    self._spotify_tracks = []
    for artist, track in desired_tracks:

      """In case artist and track are reversed, we try both queries"""
      first_query = 'artist:"%s" track:"%s"' % (artist, track)
      second_query = 'artist:"%s" track:"%s"' % (track, artist)
      queries = [first_query, second_query]

      search = self._perform_search(queries)

      if search is None:
        continue

      print '%s - %s added to playlist.' % (artist, track)
      spotify_track = search.tracks[0]
      self._spotify_tracks.append(spotify_track)

  def _collect_credentials_and_login(self):
    username = raw_input('Username: ')
    password = getpass.getpass('Password: ')

    print 'Logging in %s...' % (username)

    self._session.login(username, password)

  def user_login(self):
    print 'Please enter your Spotify credentials.\n'

    self._collect_credentials_and_login()

    try_again_count = 0

    while self._session.connection.state is not spotify.ConnectionState.LOGGED_IN:

      self._session.process_events()

      """Worth investigating a different way to do this."""
      if (try_again_count > 100000):
        print 'It seems like something is wrong with your credentials.'
        print 'Please reenter them.\n'
        self._collect_credentials_and_login()
        try_again_count = 0

      else:
        try_again_count += 1

    print 'Logged in!'

  def user_logout(self):
    print "Logging out!"
    self._session.logout()

  def generate_playlist(self, playlist_name, desired_tracks):
    print 'Searching Spotify to build %s' % playlist_name
    self._search_for_tracks(desired_tracks)
    self._generate_playlist(playlist_name)
