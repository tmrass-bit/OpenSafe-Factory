#!/usr/bin/env bash
# 사용법: bash make.sh episodes/ep01-inquiry
set -e
EP=${1:-episodes/ep01-inquiry}
NAME=$(python3 -c "import json;print(json.load(open('$EP/config.json'))['episode'])")
node render.js "$EP"                       # 1) 화면 프레임 렌더 → video_noaudio.mp4 + cues.json
python3 engine/music.py "$EP"              # 2) 타이밍(cues)에 맞춰 음악·효과음 합성 → music.wav
ffmpeg -loglevel error -y -i out/$NAME/video_noaudio.mp4 -i out/$NAME/music.wav \
  -c:v copy -c:a aac -b:a 192k -shortest out/$NAME/${NAME}_final.mp4   # 3) 합치기
echo "완성: out/$NAME/${NAME}_final.mp4"
