# from django.shortcuts import render
from googleapiclient.discovery import build,HttpError
from rest_framework.response import Response
from rest_framework.decorators import api_view
import json
import isodate
from datetime import timedelta
from url_parser import parse_url

from django.conf import settings

@api_view(['POST'])
def main(request,*args, **kwargs):
    youtube = build('youtube', 'v3',developerKey=settings.YOUTUBE_API_KEY)

    try:
        youtubeurl = request.data["youtube_url"]
        url = parse_url(youtubeurl)
        youtubeurl = url["query"]["list"]
    except KeyError:
        return Response({"success":False,"error":"invalid_url"})
    
    try:
        playlistid  = youtubeurl
        nextPageToken = None
        total_duration = timedelta(0)
        while(True):

            videos = []

            res_playlist = youtube.playlistItems().list(
                part = 'contentDetails',
                playlistId = playlistid,
                pageToken=nextPageToken,
                maxResults=50,
            ).execute()

            new_videos = [item["contentDetails"]["videoId"] for item in res_playlist["items"]]
            videos = videos + new_videos
            
            res_video = youtube.videos().list(
                part="contentDetails",
                id= ','.join(videos),
            ).execute()

            for item in res_video["items"]:
                total_duration += isodate.parse_duration(item["contentDetails"]["duration"])

            if "nextPageToken" in res_playlist:
                nextPageToken = res_playlist["nextPageToken"]
            else:
                break

        # print(total_duration.total_seconds())
        return Response({'total_duration':total_duration.total_seconds()})
            
    except HttpError as err:
        if err.resp.get('content-type', '').startswith('application/json'):
            reason = json.loads(err.content).get('error').get('errors')[0].get('reason')
            status = err.resp.status
            return Response({"succes":False,"error":reason},status=status)

        
