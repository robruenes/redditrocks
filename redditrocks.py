# redditrocks, a Spotify Playlist Generator
# requires a Spotify Premium Account, praw

import praw
import re

# Returns a list of the top num_songs (artist, song) tuples from the 
# specified music subreddit.
def scrape_submission_titles(subreddit, num_songs):
	
	tracks = []
	
	r = praw.Reddit(user_agent='redditrocks by /u/imagin4ryenemy')
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
		return (artist, song)

	except ValueError:
		return (None, None)


tracks = scrape_submission_titles('music', 10)
for (artist, song) in tracks:
	print artist + ',' + song