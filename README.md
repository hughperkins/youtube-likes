# youtube-likes

Receive a notification/email when someone 'like's one of your videos.

Target usage:
- on a system that has cron emails enabled:
  - create a cronjob, with email activated,
  - that runs this eg every 15-60 minutes
  - be sure to copy `config.yml.templ` to `config.yml`, and fill in the api key etc
  - thats it :-)

## Installation/configuration

- open a terminal. eg on a Mac, press command + space, type 'terminal', then press enter key
- clone this repo. command + spa
```
git clone https://github.com/hughperkins/youtube-likes.git
```
- cd into the `youtube-likes` folder
```
cd youtube-likes
```
- copy `config.yml.templ` to `config.yml`
```
cp config.yml.templ config.yml
```
- open config.yml in a text editor, and fill in your channel id (you can get this by going to your channel, and looking in the url, everything after `https://www.youtube.com/channel/`)
- go through steps 1-3 of https://developers.google.com/youtube/v3/getting-started
- go to credentials page https://console.cloud.google.com/apis/credentials
- at the top, click 'create credentials'
  - choose 'api key'
- copy the key, and paste it into config.yml, as the value for `api_key`
- back in credentials web page, click 'close'
- click the ... to the right of the new api key, click 'edit api key'
- change 'api restrictions' to 'restrict key'
- change 'select api' to 'youtube data api v3'
- install pyenv, and pyenv virtualenv, e.g. see
  - https://jordanthomasg.medium.com/python-development-on-macos-with-pyenv-2509c694a808
  - https://jordanthomasg.medium.com/python-development-on-macos-with-pyenv-virtualenv-ec583b92934c
- back in the terminal:
```
pyenv install 3.8.5
pyenv virtualenv 3.8.5 youtube-likes
pyenv activate youtube-likes
```

## To run

From the cloned repository:
```
pyenv activate youtube-likes
pip install -r requirements.txt
python youtube_likes.py
```

## Configuring crontab

- e.g. on some kind of shared hosting or similar, install youtube-likes, then configure crontab something like:
```
MAILTO="youremail@gmail.com"
32 * * * * nice /home/yourhome/youtube-likes/run.sh
```
- you'll need to create the script /home/hourhome/youtube-likes/run.sh, which will activate the pyenv environment, and then run   `youtube_likes.py`

## Similar projects:

- [github-stars](https://github.com/hughperkins/github-stars)
- [stackexchange-rep](https://github.com/hughperkins/stackexchange-rep)
