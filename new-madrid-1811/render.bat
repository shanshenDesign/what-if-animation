@echo off
echo Installing Node dependencies...
call npm install
if exist scripts\generate_voiceover.py (
  echo Generating free Kokoro am_fenrir voiceover if Python is available...
  python scripts\generate_voiceover.py
)
if not exist out mkdir out
echo Rendering 3D/2D Remotion video...
call npx remotion render src/index.jsx AnimatedStory out\full_silent.mp4 --gl=angle --concurrency=4 --image-format=jpeg --jpeg-quality=92 --crf=17
if exist public\voiceover.wav (
  echo Muxing Kokoro am_fenrir voiceover into final.mp4...
  call npx remotion ffmpeg -y -i out\full_silent.mp4 -i public\voiceover.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out\final.mp4
) else (
  copy /Y out\full_silent.mp4 out\final.mp4
)
echo Done! Output saved to out\final.mp4
pause
