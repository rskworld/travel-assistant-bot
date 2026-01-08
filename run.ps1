# RSK World - Free Programming Resources & Source Code
# Founder: Molla Samser | Designer & Tester: Rima Khatun
# Website: https://rskworld.in/contact.php | Year: 2026
param(
  [string]$Port = "5000"
)

Write-Host "Setting up virtual environment..." -ForegroundColor Cyan
if (!(Test-Path ".venv")) {
  python -m venv .venv
}
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

$env:PORT = $Port
Write-Host "Starting Travel Assistant Bot on port $Port..." -ForegroundColor Green
python app.py

