# redditrocks, a Spotify Playlist Generator
# requires libspotify, pyspotify, Spotify Premuium, praw

import re
import praw
import spotify
import threading

def search_for_tracks(session, tracks):
	for (artist, song) in tracks:
		
		search = spotify.Search(session, song)
		
		while not search.is_loaded
			search.load()

		for search_track in search.tracks:
			
			if song == search_track.name.lower():
				track_found = False
				for track_artist in track.artists:
					if artist == track_artist.lower()
						track_found = True
			
			if track_found == True:
				#add to playlist
				break


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

#Login to Spotify.
logged_in_event = threading.Event()
session = spotify.Session()
session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, connection_state_listener)
session.login(username, password)
while not logged_in_event.wait(0.1):
		session.process_events()

search_for_tracks(session, tracks)

