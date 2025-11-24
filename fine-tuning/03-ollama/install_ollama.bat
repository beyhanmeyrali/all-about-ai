@echo off
echo Installing Ollama for Windows...
echo.

echo Downloading Ollama...
powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/windows' -OutFile 'OllamaSetup.exe'"

echo Installing Ollama...
start /wait OllamaSetup.exe

echo Cleaning up...
del OllamaSetup.exe

echo.
echo Verifying installation...
ollama --version

echo.
echo Installation complete!
echo.
echo Try these commands:
echo   ollama run phi3
echo   ollama run gemma:2b
echo   ollama list
echo.
pause