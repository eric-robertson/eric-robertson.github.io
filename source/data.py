import os
import requests
import json
import sys
import shutil
import source.util as youtube_utils

youtube_api_base = "https://www.googleapis.com/youtube/v3"
youtube_api_keys = youtube_utils.load_api_keys()

use_key = youtube_api_keys[12]

# Utility to parse response
def youtube_api_parse ( response ) :
	if response.status_code == 200:
		return json.loads(response.text.encode("ascii", "ignore").decode("utf-8"))
	else:
		raise Exception('Token is out of API Requests')
	
# Directory processing
def dir_information ( channel_search ):
	
	dir_base = f"./youtube_data/{channel_search}"

	if not os.path.exists(dir_base): 
		os.mkdir( dir_base )
		os.mkdir( dir_base + '/videos' )
		return (True, dir_base)
	else:
		print('Channel already has saved folder, assumed finished', end = '\r')
		return (False, dir_base)

def dump_json ( data, path ):
	with open(path, 'w') as outfile:
		outfile.write(json.dumps(data))

def add_videos ( videos, channel_search ):
	dir_base = f"./youtube_data/{channel_search}"
	with open(f"{dir_base}/_videos.txt", "a") as vidFile:
		vidFile.write( '\n'.join(videos) + '\n' )

# Do search for channel
def youtube_api_search_for_channel ( channel_search ):
	return youtube_api_parse(
		requests.get( f"{youtube_api_base}/search?part=id%2Csnippet&q={channel_search}&type=channel&key={use_key}"))['items']

# Get channelid
def youtube_api_channelid ( channel_search ):
	channel = youtube_api_search_for_channel( channel_search )[0]
	return (channel, channel['id']['channelId'])
	
# Get video ids given channel id
def youtube_api_videoids ( channel_id, page = "" ):

	results = youtube_api_parse(
		requests.get( f"{youtube_api_base}/search?key={use_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=20&pageToken={page}"))

	video_ids = [ a['id']['videoId'] for a in results['items'] if a['id']['kind'] == 'youtube#video' ]
	total = results['pageInfo']['totalResults']
	next_page = ""
	finished = False
	
	if 'nextPageToken' in results:
		next_page = results['nextPageToken']
	else:
		finished = True

	return (video_ids, total, finished, next_page)

# Get video meta data given video id
def youtube_api_videometa ( video_id ):
	return youtube_api_parse(
		requests.get( f"{youtube_api_base}/videos?part=snippet,statistics&id={video_id}&key={use_key} "))
	
# Pull it all together
def youtube_api_load_videos ( channel_search ):

	(needs_processing, path) = dir_information( channel_search )

	if not needs_processing: return

	try:

		(channel, channelID) = youtube_api_channelid( channel_search )
		dump_json ( channel, path + '/_channel.json')

		finished = False
		next_page = ""
		total = 0
		video_ids = []

		while not finished:
			(_video_ids, total, finished, next_page) = youtube_api_videoids( channelID, page=next_page )
			add_videos( _video_ids, channel_search )
			if len(_video_ids) == 0:
				finished = True
			video_ids.extend( _video_ids)
			print(f"{channel_search} - Loaded {len(video_ids)} of {total} from api".ljust(100,' '), end='\r')

		for i,vid in enumerate(video_ids):
			_vid = youtube_api_videometa ( vid )
			dump_json( _vid, f"{path}/videos/{vid}.json" )
			print(f"{channel_search} - Proccessed {i} of {len(video_ids)} from api".ljust(100,' '), end='\r')
		print(f"Finished with {channel_search}".ljust(100,' '), end='\r')

	except:
		print('Failed with exception')
		shutil.rmtree(f"./youtube_data/{channel_search}")
		raise sys.exc_info()[0]

