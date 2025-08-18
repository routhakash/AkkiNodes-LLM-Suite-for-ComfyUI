@echo off
title AkkiNodes LLM Suite Installer v18.1.0 (Stable)

:: 1. Administrator Check
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    echo [INFO] Administrator privileges are required. Requesting now...
    powershell "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

cls
echo ==================================================================
echo == AkkiNodes LLM Suite Installer v18.1.0
echo ==================================================================
echo.
echo This installer will download the required Python libraries for all
echo AkkiNodes, including support for local GGUF files and LM Studio.
echo.

:: 2. Environment Activation
echo [INFO] Activating the ComfyUI Python environment...
pushd "%~dp0\..\.."
call venv\Scripts\activate.bat
echo [SUCCESS] Environment is now active.
echo.

:: 3. Clean Slate (Optional but good practice)
echo [INFO] Uninstalling any previous versions to ensure a clean install...
pip uninstall -y llama-cpp-python openai
echo.

:: 4. The Correct Installation Commands
echo [INFO] Installing required packages...
echo.
echo ---> Installing llama-cpp-python (for local GGUF models)...
pip install llama-cpp-python==0.3.9 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu122
echo.
echo ---> Installing openai (for LM Studio connection)...
pip install openai
echo.

:: 5. Final Result
if %ERRORLEVEL% EQU 0 (
    echo ==================================================================
    echo == [SUCCESS] All required libraries installed successfully!
    echo ==================================================================
) else (
    echo ==================================================================
    echo == [CRITICAL ERROR] Installation failed. Please review messages.
    echo ==================================================================
)

echo.
echo You have the complete AkkiNodes v18.1.0 package.
echo You may now close this window and restart ComfyUI.
popd
pause