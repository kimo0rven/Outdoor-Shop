@echo off
cd /d "C:\Users\kimo0\AginodOutdoorShop"

call venv\Scripts\activate

echo Launching Django Python Shell...
echo Tip: Use exit() to leave.
echo -------------------------------------------------------

python manage.py shell