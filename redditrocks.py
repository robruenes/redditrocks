# redditrocks, a Spotify Playlist Generator
# requires libspotify, pyspotify, Spotify Premuium, praw

import re
import praw
import spotify
import threading
import datetime

def tracks_added(playlist, tracks, index):
	print('Tracks added to playlist')
	tracks_added_event.set()

def search_for_tracks(session, tracks):

	playlist_tracks = []
	
	for (artist, song) in tracks:
		
		search = spotify.Search(session, song)
		
		while not search.is_loaded:
			search.load()

		for search_track in search.tracks:
			track_found = False

			# This is not robust at all. Any difference in punctuation,
			# extra info, etc. means the song doesn't get added to the 
			# playlist. This check should be replaced with a function call
			# that removes punctuation and then checks if its a substring
			if song == search_track.name.lower():
			
				for track_artist in search_track.artists:
					if artist == track_artist.name.lower():
						track_found = True
						break
			
			if track_found == True:
				playlist_tracks.append(search_track)
				break

	return playlist_tracks

def updating_playlist(playlist, done):
	if done is True:
		playlist_updated_event.set()
	
def connection_state_listener(session):
	if session.connection.state is spotify.ConnectionState.LOGGED_IN:
		logged_in_event.set()

# Returns a list of the top num_songs (artist, song) tuples from the 
# specified music subreddit.
def scrape_submission_titles(subreddit, num_songs):
	
	tracks = []
	
	r = praw.Reddit(user_agent='redditrocks')
	submissions = r.get_subreddit(subreddit).get_top(limit=num_songs)
		
	for i in range(0, num_songs):
		
		submission_title = next(submissions).title
		(artist, song) = artist_and_song(submission_title)

		if artist == None:
			num_songs += 1
			continue

		tracks.append((artist, song))

	return tracks

# Returns (artist, song) if submission_title refers to a song posting.
# Else, returns None
def artist_and_song(submission_title):
	
	artist_delimiter = re.compile(' \-* ')
	song_delimiter = re.compile(' \[')
	
	try:
		[artist, partial_title] = artist_delimiter.split(submission_title)
		[song, garbage] = song_delimiter.split(partial_title)
		return (artist.lower(), song.lower())

	except ValueError:
		return (None, None)


# Scrape /r/music for top 10 songs
tracks = scrape_submission_titles('music', 10)

username = 'your username here'
password = 'your password here'

#Threads
logged_in_event = threading.Event()
playlist_updated_event = threading.Event()
playlist_loaded_event = threading.Event()
tracks_added_event = threading.Event()

#Login to Spotify
session = spotify.Session()
session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, connection_state_listener)
session.login(username, password)

while not logged_in_event.wait(0.1):
		session.process_events()

spotify_tracks = search_for_tracks(session, tracks)

playlists = session.playlist_container
playlist = playlists.add_new_playlist("RedditRocks Top Ten")
playlist.on(spotify.PlaylistEvent.TRACKS_ADDED, tracks_added)
playlist.on(spotify.PlaylistEvent.PLAYLIST_UPDATE_IN_PROGRESS, updating_playlist)
playlist.add_tracks(spotify_tracks)
playlist.load()

while not tracks_added_event.wait(0.1):
	session.process_events()

while not playlist_updated_event.wait(0.1):
	session.process_events()

print "Done."
session.logout()


