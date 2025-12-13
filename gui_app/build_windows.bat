@echo off
REM Build script for Windows
echo Building Face Recognition App for Windows...

REM Detect if we're in a virtual environment
if defined VIRTUAL_ENV (
    echo Using virtual environment: %VIRTUAL_ENV%
    set PYTHON_CMD=python
    set PIP_CMD=pip
) else (
    echo Using system Python
    set PYTHON_CMD=python
    set PIP_CMD=pip
)

REM Check if PyInstaller is installed
%PYTHON_CMD% -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    %PIP_CMD% install pyinstaller
)

REM Create build directory
if not exist "dist" mkdir dist
if not exist "build" mkdir build

REM Build executable
echo Running PyInstaller...
%PYTHON_CMD% -m PyInstaller --clean build.spec

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Executable is in: dist\FaceRecognitionApp.exe
echo.
pause

