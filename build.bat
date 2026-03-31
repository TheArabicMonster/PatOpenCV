@echo off
REM Build PatOpenCV → PatOpenCV.exe (Windows)

echo === PatOpenCV Build (Windows) ===

pip install pyinstaller --quiet
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

pyinstaller PatOpenCV.spec

echo.
echo OK  dist\PatOpenCV.exe  -^>  double-clic pour lancer
echo     Pour distribuer : zipper le dossier dist\
pause
