#!/usr/bin/env python

"""
RedditRocks - a Spotify Playlist Generator
Creates Spotify playlist based on music subreddits
"""

# Created by Rob Ruenes <robruenes@gmail.com> on 5/13/2014, updated 8/14/2014
#
# Notes:
# - Requires a Spotify Premium account
# - Requires libspotify (https://developer.spotify.com/technologies/libspotify/)
# - Requires pyspotify (https://github.com/mopidy/pyspotify)
# - Requires a spotify_appkey.key in the same directory as this file.
#   Can be obtained at https://devaccount.spotify.com/my-account/keys/

import re
import praw
import datetime
import playlistgenerator

"""Scrapes reddit for tracks, uses playlist generator to build playlist"""
class RedditRocks(object):

  def __init__(self):
    self._song_count = None
    self._subreddits = ['music', 'posthardcore']
    self._tracks = []
    self._requested_subreddits = []
    self._reddit = praw.Reddit(user_agent="RedditRocks")
    self._playlist_generator = playlistgenerator.SpotifyPlaylistGenerator()

  def _get_music_songs(self):
    """Post format: Artist - Title [Genre] Extra Text"""
    pattern = '([^-]*)-+([^-]*)\['

    submissions = self._reddit.get_subreddit('music').get_top(limit=None)

    for submission in submissions:

      search = re.search(pattern, submission.title)

      if search:
        self._tracks.append((search.group(1).strip(), search.group(2).strip()))

  def _get_songs(self, subreddit):
    if subreddit == 'music':
      return self._get_music_songs()

  def _prompt_for_subreddits(self):
    print 'Which subreddits would you like music from?'

    for subreddit in self._subreddits:
      print subreddit

    request_string = raw_input('Please enter their names separated by commas: ')

    for subreddit in request_string.split(','):

      if subreddit.strip().lower() not in self._subreddits:
        print '%s is not a valid subreddit.' % (subreddit)

      else:
        self._requested_subreddits.append(subreddit.strip())


  def _generate_playlists(self):
    for subreddit in self._requested_subreddits:

      self._tracks = []
      self._get_songs(subreddit)

      date_string = datetime.datetime.now().strftime('%I:%M%p on %B %d, %Y')
      playlist_name = 'r/%s top songs at %s' % (subreddit, date_string)

      self._playlist_generator.generate_playlist(playlist_name, self._tracks)

  def run(self):
    print 'Thanks for using RedditRocks!'

    self._playlist_generator.user_login()
    self._prompt_for_subreddits()
    self._generate_playlists()
    self._playlist_generator.user_logout()

def main():
  redditrocks = RedditRocks()
  redditrocks.run()

if __name__ == "__main__":
  main()
