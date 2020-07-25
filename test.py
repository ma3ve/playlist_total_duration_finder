from googleapiclient.discovery import build,HttpError
import json
import isodate
from datetime import timedelta

youtube = build('youtube', 'v3',developerKey ='AIzaSyAfPttVMOYuyRJaGq2jqHmKsNfbKRjXRc4')
try:
    playlistid  = 'PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU'
    #getting list of videos
    nextPageToken = None
    videos = []
    while(True):
        res = youtube.playlistItems().list(
            part = 'contentDetails',
            playlistId = playlistid,
            pageToken=nextPageToken,
        ).execute()

        new_videos = [item["contentDetails"]["videoId"] for item in res["items"]]
        videos = videos + new_videos
        if nextPageToken in res:
            nextPageToken = res["nextPageToken"]
        else:
            break

    total_duration = timedelta(0)

    nextPageToken = None
    while True:
        res = youtube.videos().list(
            part="contentDetails",
            id= ','.join(videos)
        ).execute()
        
        for item in res["items"]:
            total_duration += isodate.parse_duration(item["contentDetails"]["duration"])
            print(total_duration)
        if nextPageToken in res:
            nextPageToken = res["nextPageToken"]
        else:
            break
    
except HttpError as err:
    if err.resp.get('content-type', '').startswith('application/json'):
        reason = json.loads(err.content).get('error').get('errors')[0].get('reason')
        status = err.resp.status
        print(reason)