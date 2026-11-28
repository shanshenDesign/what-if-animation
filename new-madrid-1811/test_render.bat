@echo off
call npm install
if not exist out mkdir out
call npx remotion render src/index.jsx AnimatedStory out\test_30f.mp4 --frames=0-29 --gl=angle
echo 30-frame test complete: out\test_30f.mp4
pause
