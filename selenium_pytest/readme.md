# Install dependencies:
pip install -r requirements.txt

# Run tests:
python -m tests/<.py file>

# Test Configuration
The test configuration allows for customization of the browser environment by specifying parameters in the config.env file.

## Browser Selection
You can define the desired browser by specifying its name in the config.env file.

## Additional Configuration Options
Base URL
Define the base URL for your tests in the config.env file.

## Headless Mode 
Specify whether the browser should start in headless mode or not by setting the appropriate flag in the config.env file.