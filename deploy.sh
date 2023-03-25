echo Create virtual environment
python3.8 -m venv test_env
echo Activate virtual environment
source ./test_env/bin/activate
echo Installing all dependencies
pip install -e .
echo Migrating database...
alembic upgrade head
echo Done! Running application...
run_app