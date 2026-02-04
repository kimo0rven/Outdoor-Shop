@echo off
:: Prevents the script from calling itself if named similarly
setlocal

cd /d "C:\Users\kimo0\AginodOutdoorShop"

:: Check if venv exists before calling
if exist venv\Scripts\activate (
    call venv\Scripts\activate
) else (
    echo Virtual environment not found!
    pause
    exit /b
)

cls
echo =======================================================
echo  AGINOD OUTDOOR SHOP - MANAGEMENT TERMINAL
echo =======================================================
echo.
echo  Commands you can run:
echo  - python manage.py makemigrations
echo  - python manage.py migrate
echo  - python manage.py createsuperuser
echo.
echo  Type 'exit' to close this window.
echo -------------------------------------------------------

:: Use /k to keep the session open and active
cmd /k