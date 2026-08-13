@echo off
cd /d "C:\Users\amiza\Desktop\garmin-dashboard"
echo ---- %date% %time% ---- >> dashboard_push.log
"C:\Users\amiza\AppData\Local\Programs\Python\Python314\python.exe" dashboard.py >> dashboard_push.log 2>&1
