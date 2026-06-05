@echo off
echo Memulai instalasi Nuitka...
e:\dev\venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo Memulai kompilasi ML Agents Universe dengan Nuitka (Standalone)...
echo Peringatan: Proses ini bisa memakan waktu 10-30 menit tergantung spesifikasi sistem.
echo.

e:\dev\venv\Scripts\python.exe -m nuitka ^
  --standalone ^
  --enable-plugin=pyside6 ^
  --include-package=langchain ^
  --include-package=langchain_core ^
  --include-package=langchain_community ^
  --include-package=langgraph ^
  --include-package=pydantic ^
  --include-package=sqlalchemy ^
  --include-package=psutil ^
  --include-package=agents ^
  --include-package=shared ^
  --include-package=ui ^
  --include-package=scripts ^
  --follow-imports ^
  --nofollow-import-to=faiss ^
  --nofollow-import-to=torch ^
  --output-dir=build_dist ^
  run_desktop.py

echo.
echo Proses kompilasi selesai. Silakan periksa folder build_dist\run_desktop.dist\
pause
