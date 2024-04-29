# Install dependencies:
pip install -r requirements.txt

# Install playwright:
playwright install

# Run tests:
python -m pytest tests/<.py file>

# Specify browser
python -m pytest --browser <browser_name> tests/<.py file>\
E.g: 
python -m pytest --browser firefox tests/<.py file>

# Screenshots on failure
python -m pytest --screenshot only-on-failure <browser_name> tests/<.py file>\