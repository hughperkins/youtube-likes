"""
Before running this, you should follow the instructions in get_refresh_token.py
"""
import argparse
import json

# import time
# import warnings
# from os import path
# import email.message
# from email.mime.text import MIMEText
# import smtplib

import os

# import google.oauth2.credentials
# import google_auth_oauthlib.flow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from googleapiclient.http import MediaIoBaseDownload
# from google_auth_oauthlib.flow import InstalledAppFlow
# from io import FileIO

import requests
from ruamel.yaml import YAML

yaml = YAML()
# warnings.simplefilter("ignore", yaml.error.UnsafeLoaderWarning)

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for read access to YouTube Analytics
# monetary reports for the authenticated user's account. Any request that
# retrieves earnings or ad performance metrics must use this scope.
# SCOPES = ["https://www.googleapis.com/auth/yt-analytics-monetary.readonly"]
SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly"]
API_SERVICE_NAME = "youtubereporting"
API_VERSION = "v1"


# # Authorize the request and store authorization credentials.
# def get_authenticated_service():
#     flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
#     credentials = flow.run_console()
#     return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)


# def send_email(
#     smtp_server,
#     smtp_port,
#     username,
#     password,
#     from_email,
#     to_email,
#     subject,
#     message,
# ):
#     # msg = email.message.EmailMessage()
#     msg = MIMEText(
#         "<html><body>"
#         + message.replace(" ", "&nbsp;").replace("\n", "<br />")
#         + "</body></html>",
#         "html",
#     )
#     msg["Subject"] = subject
#     msg["From"] = from_email
#     msg["To"] = to_email
#     # msg.set_content(message)

#     with smtplib.SMTP(smtp_server, smtp_port) as smtp:
#         smtp.login(username, password)
#         smtp.sendmail(from_email, to_email, msg.as_string())


def refresh_access_token(client_id, client_secret, refresh_tkn):
    url = "https://accounts.google.com/o/oauth2/token"
    print("client_id", client_id)
    print("client_secret", client_secret)
    print("refresh_tkn", refresh_tkn)
    data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_tkn,
    }
    headers = {"content-type": "application/x-www-form-urlencoded"}

    d = requests.post(url, data=data, headers=headers).json()
    print("d", d)
    return d["token_type"], d["access_token"]


def run(args):
    with open(args.config_file, "r") as f:
        config = yaml.load(f)
    # print('config', config)

    # email_message = ""

    # youtube_reporting = get_authenticated_service()
    # print('youtube_reporting', youtube_reporting)

    # results = youtube_reporting.jobs().reports().list().execute()
    # print('results', results)

    # api_key = config["api_key"]

    token_type, access_token = refresh_access_token(
        config["google_client_id"],
        config["google_client_secret"],
        config["google_refresh_token"],
    )
    print("access_token", token_type, access_token)
    auth_headers = {"Authorization": f"{token_type} {access_token}"}

    # res = requests.get(
    #     'https://youtubeanalytics.googleapis.com/v2/reports', headers={
    #         'Authorization': f'{token_type}: {access_token}'
    #     })
    # if res.status_code != 200:
    #     print("res.status_code %s" % res.status_code)
    #     print(res.content)
    #     raise Exception("invalid status code %s" % res.status_code)

    reporting_job_id = config["reporting_job_id"]
    print("reporting_job_id", reporting_job_id)
    res = requests.get(
        f"https://youtubereporting.googleapis.com/v1/jobs/{reporting_job_id}/reports",
        headers=auth_headers,
    )
    if res.status_code != 200:
        print("res.status_code %s" % res.status_code)
        print(res.content)
        raise Exception("invalid status code %s" % res.status_code)
    d = json.loads(res.content.decode("utf-8"))
    print(d)

    for rep in d["reports"]:
        print(rep)
        url = rep["downloadUrl"]
        res = requests.get(url, headers=auth_headers)
        if res.status_code != 200:
            print("res.status_code %s" % res.status_code)
            print(res.content)
            raise Exception("invalid status code %s" % res.status_code)
        print(res.content.decode("utf-8"))
        with open(args.out_csv, "w") as f:
            f.write(res.content.decode("utf-8"))
            os.system(f" open {args.out_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", default="config.yml", type=str)
    parser.add_argument("--out-csv", default="/tmp/foo.csv", type=str)
    # parser.add_argument("--no-send", action="store_true")
    args = parser.parse_args()
    run(args)
