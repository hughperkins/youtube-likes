"""
Based on https://github.com/d4vidsha/python-requests-to-google-sheets-api/blob/master/get-refresh-token.py
"""
# import requests
import argparse
import os
from ruamel.yaml import YAML


yaml = YAML()


# step 1: fill in the client credentials, in config.yml
# google_client_id: "999[redacted]pbub.apps.googleusercontent.com"
# google_client_secret: "[redacted]"


# step 2: get a temporary access code manually
# run this script
#
# python get_refresh_token.py
#
# in the web browser, work through the prompts
# the final url contains the acces code, e.g. if the url is
# http://localhost/?code=4/0AfJohXnTN[redacted]&scope=https://www.googleapis.com/auth/yt-analytics.readonly
#
# ... then the code is: 4/0AfJohXnTN[redacted]
# (basically from 'code= up to '&scope')
#
# step 3: add this token into your config.yml:
#
# google_refresh_token: '4/0AfJohXl2[redacted]'
#
# You should be good :)
def main(args):
    scope = "https://www.googleapis.com/auth/yt-analytics.readonly"

    with open("config.yml") as f:
        config = yaml.load(f)

    # access_code = args.access_code
    # if args.access_code is None:
    # async def got_token(request):
    #     nonlocal access_code
    #     access_code = request.rel_url.query['code']
    #     print('access_code', access_code)
    #     return web.Response(text="Ok")
    #     # raise GracefulExit()

    # app = web.Application()
    # app.add_routes([web.get('/', got_token)])

    # get refresh token/access token from access code
    client_id = config["google_client_id"]

    auth_url = (
        "https://accounts.google.com/o/oauth2/auth?access_type=offline&approval_prompt=auto&"
        f"client_id={client_id}&response_type=code&scope={scope}&redirect_uri=http://localhost"
    )
    print(auth_url)
    os.system(f"open '{auth_url}'")
    # web.run_app(app, host='localhost', port=args.local_port)
    return

    # print('access_code', access_code)

    # url = "https://accounts.google.com/o/oauth2/token"
    # data = {
    #     "grant_type": "authorization_code",
    #     "code": access_code,
    #     "client_id": config['google_client_id'],
    #     "client_secret": config['google_client_secret'],
    #     "scope": scope,
    #     "redirect_uri": "http://localhost"
    # }
    # headers = {
    #     "content-type": "application/x-www-form-urlencoded"
    # }

    # r = requests.request('POST', url, data=data, headers=headers)
    # print(r.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument('--access-code', type=str)
    # parser.add_argument('--local-port', type=int, default=80)
    args = parser.parse_args()
    main(args)
