"""
Based on https://developers.google.com/youtube/reporting/v1/code_samples/python#retrieve_daily_channel_statistics

Make sure to enable the analytics api inside google cloud console first
"""
import argparse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.http import MediaIoBaseDownload
from io import FileIO


SCOPES = ['https://www.googleapis.com/auth/yt-analytics.readonly']

API_SERVICE_NAME = 'youtubereporting'
API_VERSION = 'v1'
CLIENT_SECRETS_FILE = 'client_secret.json'


def get_service(port: int):
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=port)
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


# def execute_api_request(client_library_function, args, **kwargs):
#     response = client_library_function(
#         **kwargs
#     ).execute()

#     print(response)
#     for report in response['reports']:
#         print(report['id'], report['jobId'], report['startTime'], report['endTime'], report['downloadUrl'])


# Call the YouTube Reporting API's media.download method to download the report.
def download_report(youtube_reporting, report_url, local_file):
    request = youtube_reporting.media().download(
        resourceName=' '
    )
    request.uri = report_url
    fh = FileIO(local_file, mode='wb')
    # Stream/download the report in a single request.
    downloader = MediaIoBaseDownload(fh, request, chunksize=-1)

    done = False
    while done is False:
        status, done = downloader.next_chunk()
        if status:
            print('Download %d%%.' % int(status.progress() * 100))
    print('Download Complete!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    # parser.add_argument('--job-id', type=str, required=True)
    parser.add_argument('--url', type=str, required=True)
    parser.add_argument('--out-file', type=str, required=True)
    args = parser.parse_args()

    youtube_reporting = get_service(port=args.port)
    download_report(youtube_reporting, args.url, args.out_file)
    # execute_api_request(
    #     youtube_reporting.jobs().reports().list,
    #     args=args,
    #     jobId=args.job_id
    # )
