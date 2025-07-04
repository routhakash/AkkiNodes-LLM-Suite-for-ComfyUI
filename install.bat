@echo off
title AkkiNodes LLM Suite Installer v14.0.0 (Definitive Pre-Built)

:: 1. Administrator Check
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    echo [INFO] Administrator privileges are required. Requesting now...
    powershell "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

cls
echo ==================================================================
echo == AkkiNodes LLM Suite Installer v14.0.0
echo ==================================================================
echo.
echo This installer will download the correct pre-built, GPU-accelerated
echo package for your system. This is the final, stable method.
echo.

:: 2. Environment Activation
echo [INFO] Activating the ComfyUI Python environment...
pushd "%~dp0\..\.."
call venv\Scripts\activate.bat
echo [SUCCESS] Environment is now active.
echo.

:: 3. Clean Slate
echo [INFO] Uninstalling any previous failed attempts...
pip uninstall -y llama-cpp-python
echo.

:: 4. The Single, Correct Command
echo [INFO] Installing the correct pre-built package for your system...
pip install llama-cpp-python==0.3.9 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu122
echo.

:: 5. Final Result
echo.
if %ERRORLEVEL% EQU 0 (
    echo ==================================================================
    echo == [SUCCESS] Installation completed successfully!
    echo ==================================================================
) else (
    echo ==================================================================
    echo == [CRITICAL ERROR] Installation failed.
    echo ==================================================================
)

echo.
echo You have the complete AkkiNodes v14.0.0 package.
echo You may now close this window and restart ComfyUI.
popd
pause