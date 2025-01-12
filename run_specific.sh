#!/bin/bash

export HOME=/persist
cd
. ~/.pyenv/activate
pyenv activate nfs-youtube-likes-10
# source ~/.bashrc
cd ~/git/youtube-likes
if ps -ef | grep check_specific_videos.py | grep -v grep > /dev/null; then {
	echo "ycheck_specific_videos already running"
	exit 1
} fi

echo "check_specific_videos not running"

# ps -ef | grep youtube_likes.py | grep -v grep | awk '{print $2;}' | xargs -L1 kill
python check_specific_videos.py $*
