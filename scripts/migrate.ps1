# Run Alembic upgrade head using the project's Python
$venvPython = "$PSScriptRoot\..\backend\.venv\Scripts\python.exe"
if (Test-Path $venvPython) {
  & $venvPython "$PSScriptRoot\..\backend\migrate.py"
} else {
  python "$PSScriptRoot\..\backend\migrate.py"
}
