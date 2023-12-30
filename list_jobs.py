"""
Based on https://developers.google.com/youtube/reporting/v1/code_samples/python#retrieve_daily_channel_statistics

Make sure to enable the analytics api inside google cloud console first
"""
import argparse
import csv
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ['https://www.googleapis.com/auth/yt-analytics.readonly']

API_SERVICE_NAME = 'youtubereporting'
API_VERSION = 'v1'
CLIENT_SECRETS_FILE = 'client_secret.json'


def get_service(port: int):
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=port)
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def execute_api_request(client_library_function, args, **kwargs):
    response = client_library_function(
        **kwargs
    ).execute()

    print(response)
    for job in response['jobs']:
        print(job['id'], job['name'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()

    youtube_reporting = get_service(port=args.port)
    execute_api_request(
        youtube_reporting.jobs().list,
        args=args
    )
