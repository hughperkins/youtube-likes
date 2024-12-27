#!/bin/bash

export HOME=/persist
cd
. ~/.pyenv/activate
pyenv activate nfs-youtube-likes
# source ~/.bashrc
cd ~/git/youtube-likes
if ps -ef | grep youtube_likes.py | grep -v grep > /dev/null; then {
	echo "youtube likes already running"
	exit 1
} fi

echo "youtube likes not running"

# ps -ef | grep youtube_likes.py | grep -v grep | awk '{print $2;}' | xargs -L1 kill
python youtube_likes.py $*
