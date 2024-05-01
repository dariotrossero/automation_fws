# Install dependencies:
pip install -r requirements.txt

# Install playwright:
playwright install

# Run tests:
python -m pytest tests/<.py file>

# Specify browser
python -m pytest --browser <browser_name> tests/<.py file>\
<browser_name> can be firefox, chromium and webkit\
To execute the tests in microsoft edge add\
--browser chromium --browser-channel msedge\
E.g:\
python -m pytest --browser firefox tests/<.py file>\
python -m pytest --browser chromium tests/<.py file>\
python -m pytest --browser chromium --browser-channel msedge tests/<.py file>\
python -m pytest --browser webkit/<.py file>\

# Screenshots on failure
python -m pytest --screenshot only-on-failure <browser_name> tests/<.py file>\
