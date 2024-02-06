chcp 65001
@echo off
rem echo PYTHONPATH contains: %PYTHONPATH%

rem for /f "tokens=*" %%i in ('echo %PYTHONPATH%') do set PythonPath=%%i
rem echo PythonPath contains: %PythonPath%

set "telloconsole=Tello-Console2\tello_console2"

echo %PYTHONPATH% | find "%telloconsole%" > nul
if %errorlevel% equ 0 (
    echo TELLO-CONSOLE2 is already added in PYTHONPATH
) else (
    setx PYTHONPATH "%PYTHONPATH%;%USERPROFILE%\Tello-Console2\tello_console2"
    start cmd /c python -c "from console import Console"
)

:LOOP
set "downloadPath=%USERPROFILE%\Downloads"
set "ffmpeg_zip_path="

for %%I in ("%downloadPath%\ffmpeg*.zip") do (
    if exist "%%I" (
        set "ffmpeg_zip_path=%%~fI"
        goto :FOUND
    )
)

echo Waiting for ffmpeg zip file in Downloads...
timeout /nobreak /t 5 > nul 2>&1
goto LOOP

:FOUND
echo Found ffmpeg zip file at: %ffmpeg_zip_path%

echo %PATH% | find "ffmpeg" > nul
if %errorlevel% equ 0 (
    set "ffmpeg_in_path=1"
    echo 'ffmpeg' found in PATH.
) else (
    echo 'ffmpeg' not found in PATH.
)

set "extractPath=%USERPROFILE%"
set "ffmpeg_dir_exists="
set "ffmpegDirectory="

:CHECK_DIR
for /d %%D in ("%extractPath%\ffmpeg*") do (
    set "ffmpeg_dir_exists=1"
    set "ffmpegDirectory=%%~fD\bin"
    goto :BREAK_LOOP
)

:BREAK_LOOP
if defined ffmpeg_dir_exists (
    echo ffmpeg directory found in %ffmpegDirectory%
    echo 以下のパスを環境変数PATHに追加してください！
    echo %ffmpegDirectory%

    goto :END
) else (
    echo ffmpeg directory not found in %extractPath%.
    powershell -Command "Expand-Archive -Path '%ffmpeg_zip_path%' -DestinationPath '%extractPath%' -Force"
    goto :CHECK_DIR
)

:END
echo Done !