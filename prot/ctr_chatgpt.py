# https://chatgpt.com/c/678bbcbd-ccb4-8012-a9ac-73ed56fdcf90
import argparse
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly"]


def authenticate_and_get_service(credentials_path):
    """
    Authenticate using OAuth 2.0 credentials and return a YouTube Analytics API service instance.
    """
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    credentials = flow.run_local_server(port=0)
    service = build('youtubeAnalytics', 'v2', credentials=credentials)
    return service


def get_video_ctr(service, video_id, start_date, end_date):
    """
    Fetch Click-Through Rate (CTR) data for a given video ID and date range.
    """
    request = service.reports().query(
        startDate=start_date,
        endDate=end_date,
        metrics="impressions,views",
        ids='channel==MINE',
        dimensions="video",
        filters=f"video=={video_id}"
    )
    response = request.execute()
    return response


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Fetch YouTube video CTR data using OAuth 2.0.")
    parser.add_argument("--video-id", required=True, help="The ID of the YouTube video.")
    parser.add_argument("--start-date", required=True, help="Start date for the data in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date for the data in YYYY-MM-DD format.")
    parser.add_argument("--credentials", required=True, help="Path to the OAuth 2.0 client JSON credentials file.")
    
    args = parser.parse_args()

    try:
        # Authenticate and create a service instance
        service = authenticate_and_get_service(args.credentials)
        # Fetch CTR data
        ctr_data = get_video_ctr(service, args.video_id, args.start_date, args.end_date)
        print("CTR Data:", ctr_data)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
