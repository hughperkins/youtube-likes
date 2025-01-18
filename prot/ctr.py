# from https://claude.ai/chat/e1259864-bbb2-41b4-8887-2597106e0f9a
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime, timedelta
import pandas as pd
import argparse
import sys

SCOPES = ['https://www.googleapis.com/auth/yt-analytics.readonly']


def get_youtube_analytics(client_secrets_path):
    """
    Fetch Click Through Rate (CTR) data from YouTube Analytics API
    
    Args:
        client_secrets_path (str): Path to the client secrets JSON file
    
    Returns:
        DataFrame with video titles and their CTR
    """
    try:
        # OAuth 2.0 flow to get credentials
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_path,
            SCOPES
        )
        credentials = flow.run_local_server(port=0)
    except FileNotFoundError:
        print(f"Error: Could not find client secrets file at {client_secrets_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during authentication: {str(e)}")
        sys.exit(1)
    
    # Build the YouTube Analytics API service
    youtube_analytics = build('youtubeAnalytics', 'v2', credentials=credentials)
    
    # Calculate date range (last 28 days)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=28)).strftime('%Y-%m-%d')
    
    # Make the API request
    request = youtube_analytics.reports().query(
        dimensions='video',
        metrics='impressionClickRate,impressions,views',
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        sort='-impressionClickRate'
    )
    
    response = request.execute()
    
    # Convert the response to a DataFrame
    if 'rows' in response:
        df = pd.DataFrame(
            response['rows'],
            columns=['video_id', 'ctr', 'impressions', 'views']
        )
        
        # Get video titles using YouTube Data API
        youtube = build('youtube', 'v3', credentials=credentials)
        
        def get_video_title(video_id):
            request = youtube.videos().list(
                part='snippet',
                id=video_id
            )
            response = request.execute()
            return response['items'][0]['snippet']['title']
        
        df['title'] = df['video_id'].apply(get_video_title)
        df['ctr'] = df['ctr'].apply(lambda x: f"{x:.2%}")
        
        return df[['title', 'ctr', 'impressions', 'views']]
    
    return pd.DataFrame()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Fetch YouTube Analytics CTR data for your channel'
    )
    parser.add_argument(
        '--secrets',
        required=True,
        help='Path to the client_secrets.json file from Google Cloud Console'
    )
    return parser.parse_args()


if __name__ == "__main__":
    try:
        args = parse_arguments()
        df = get_youtube_analytics(args.secrets)
        if not df.empty:
            print("\nYouTube Video CTR Report")
            print("=======================")
            print(df.to_string(index=False))
        else:
            print("No data found for the specified period.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
