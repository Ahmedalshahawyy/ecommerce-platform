# Run backend tests via venv python if available
$venvPy = "$PSScriptRoot\..\backend\.venv\Scripts\python.exe"
if (Test-Path $venvPy) {
  & $venvPy -m pytest -q ..\backend\tests
} else {
  python -m pytest -q backend\tests
}
