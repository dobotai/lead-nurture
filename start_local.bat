@echo off
echo Starting Lead Nurture System (Local)
echo =====================================
echo.
echo Starting webhook server on port 8080...
start "Webhook Server" cmd /k python execution\webhook_server.py 8080
echo.
echo Starting orchestrator (checks every 5 minutes)...
start "Orchestrator" cmd /k python execution\lead_nurture_orchestrator.py --continuous 300
echo.
echo Both services started!
echo.
echo Webhook endpoint: http://localhost:8080/enroll
echo Health check: http://localhost:8080/health
echo.
echo Press Ctrl+C in each window to stop the services.
pause
