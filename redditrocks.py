#!/usr/bin/env python

"""
RedditRocks - a Spotify Playlist Generator
Creates a playlist in Spotify from the top posts on /r/music
"""

# Created by Rob Ruenes <robruenes@gmail.com> on 5/13/2014
#
# Notes:
# - Requires a Spotify Premium account
# - Requires libspotify (https://developer.spotify.com/technologies/libspotify/)
# - Requires pyspotify (https://github.com/mopidy/pyspotify)  
# - Requires a spotify_appkey.key in the same directory as this file.
#   Can be obtained at https://devaccount.spotify.com/my-account/keys/

import re
import praw
import spotify
import threading
import getpass
import datetime

"""The RedditPlaylistCreator class is responsible for the bulk of the work, 
   as it scrapes /r/music for the top submissions and then searches Spotify
   for those tracks. It then builds a playlist out of all succesfully 
   discovered tracks"""
class RedditPlaylistCreator(object):

    def __init__(self, session, song_count):

        self._song_count = song_count

        # Spotify related
        self._session = session
        self._playlist_created = threading.Event()
        self._spotify_tracks = []
        self._tracks_added_event = threading.Event()
        self._playlist_updated_event = threading.Event()

        # Reddit related
        self._reddit = praw.Reddit(user_agent='RedditRocks')
        self._artist_delimiter = re.compile(' \-* ')
        self._track_delimiter = re.compile(' \[')
        self._tracks_from_reddit = []
        self._subreddit = 'music'
        self._num_subs = self._song_count * 2

    def _tracks_added(self, playlist, tracks, index):

        print('Tracks added to playlist.')
        self._tracks_added_event.set()

    def _updating_playlist(self, playlist, done):

        if done is True:
            self._playlist_updated_event.set()

    def _scrape_submission_titles(self):

        submissions = self._reddit.get_subreddit(self._subreddit).get_top(limit=self._num_subs)

        for i in range(1, self._num_subs):
            
            submission = next(submissions).title
            (artist, track) = self._artist_and_track(submission)
            
            if artist is not None:
            
                self._tracks_from_reddit.append((artist, track))
            
    def _artist_and_track(self, submission):
        
        try:
            [artist, partial_title] = self._artist_delimiter.split(submission)
            [track, garbage] = self._track_delimiter.split(partial_title)
            return (artist, track)

        except ValueError:
            return (None, None)

    def _search_for_tracks(self):

        tracks_discovered = 0

        for (artist, track) in self._tracks_from_reddit:
            
            print "Searching for %s - %s." % (artist, track)
            query = 'artist:"%s" title:"%s"' % (artist, track)
            search = spotify.Search(self._session, query)
            
            while not search.is_loaded:
                search.load()

            if search.track_total < 1:
                print 'Could not find %s - %s.' % (artist, track)
                continue 

            print '%s - %s was found.' % (artist, track)    
            spotify_track = search.tracks[0]
            self._spotify_tracks.append(spotify_track)
            tracks_discovered += 1

            if tracks_discovered == self._song_count: break

    def _build_playlist(self, name):
        
        playlist = self._session.playlist_container.add_new_playlist(name)
        playlist.on(spotify.PlaylistEvent.TRACKS_ADDED, self._tracks_added)
        playlist.on(spotify.PlaylistEvent.PLAYLIST_UPDATE_IN_PROGRESS, self._updating_playlist)
        
        print "Building playlist with discovered tracks."
        playlist.add_tracks(self._spotify_tracks)
        playlist.load()

        while not self._tracks_added_event.wait(0.1):
            self._session.process_events()

        while not self._playlist_updated_event.wait(0.1):
            self._session.process_events()

        print "Playlist built!"

    def create_playlist(self):
        
        self._scrape_submission_titles()
        self._search_for_tracks()
       
        if self._spotify_tracks:

            date_string = datetime.datetime.now().strftime('%I:%M%p on %B %d, %Y')
            self._build_playlist("RedditRocks at " + date_string)
       
        else:
            print "No songs found on Spotify. Will not build playlist."


"""The RedditRocks class is responsible for setting up the Spotify session and then
   creating an instance of the RedditPlaylistCreator class to build the playlist"""
class RedditRocks(object):

    def __init__(self):
       
        self._logged_in_event = threading.Event()
        self._session = spotify.Session()
        self._session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, self._connection_state_listener)
        self._song_count = None

    def _connection_state_listener(self, session):
       
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            self._logged_in_event.set()

    def _login(self, username='', password=''):
       
        self._session.login(username, password)
        while not self._logged_in_event.wait(0.1):
            self._session.process_events()

    def _create_playlist(self):
       
        creator = RedditPlaylistCreator(self._session, self._song_count)
        creator.create_playlist()

    def run(self):
        
        username = raw_input('Spotify Username: ')
        password = getpass.getpass('Spotify Password: ')

        try:
            self._song_count = int(raw_input('Number of tracks for playlist: '))

            print "Logging in..."
            self._login(username, password)
            print "Logged in!"

            print "Building playlist..."
            self._create_playlist()

            print "Logging out..."
            self._session.logout()

        except ValueError:
            print 'Input was not a number. Quitting...'

def main():
    redditrocks = RedditRocks()
    redditrocks.run()

if __name__ == "__main__":
    main()