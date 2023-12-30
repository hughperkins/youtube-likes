"""
Based on https://developers.google.com/youtube/reporting/v1/code_samples/python#retrieve_daily_channel_statistics
"""
# import os
# import google.oauth2.credentials
# import google_auth_oauthlib.flow
import argparse
import csv
import os
from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ['https://www.googleapis.com/auth/yt-analytics.readonly']

API_SERVICE_NAME = 'youtubeAnalytics'
API_VERSION = 'v2'
CLIENT_SECRETS_FILE = 'client_secret.json'


def get_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server()
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def execute_api_request(client_library_function, args, **kwargs):
    response = client_library_function(
        **kwargs
    ).execute()

    print(response)
    if args.out_csv is not None:
        field_names = [col['name'] for col in response['columnHeaders']]
        print('field_names', field_names)
        with open(args.out_csv, 'w') as f:
            dict_writer = csv.DictWriter(f, fieldnames=field_names)
            dict_writer.writeheader()
            for row in response['rows']:
                row_dict = {field_name: value for field_name, value in zip(field_names, row)}
                dict_writer.writerow(row_dict)
        print('wrote', args.out_csv)
        os.system(f'open {args.out_csv}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-date', type=str, required=True, help='yyyy-mm-dd')
    parser.add_argument('--end-date', type=str, required=True, help='yyyy-mm-dd')
    parser.add_argument('--out-csv', type=str)
    args = parser.parse_args()
    # Disable OAuthlib's HTTPs verification when running locally.
    # *DO NOT* leave this option enabled when running in production.
    # os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    youtubeAnalytics = get_service()
    execute_api_request(
        youtubeAnalytics.reports().query,
        args=args,
        ids='channel==MINE',
        startDate=args.start_date,
        endDate=args.end_date,
        metrics='estimatedMinutesWatched,views,likes,subscribersGained',
        dimensions='day',
        sort='day'
    )
