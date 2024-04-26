import logging
import os
from pathlib import Path

from dotenv import load_dotenv


class Config:
    logging.getLogger('Config')

    # Loads all the environment variables from conf/secret.env file.
    load_dotenv(dotenv_path=Path(os.path.join(os.path.dirname(__file__), "config.env")))

    @classmethod
    def _get_property(cls, property_name):
        """
        Get the value of the specified property from environment variables.

        Args:
            property_name (str): Name of the property.

        Returns:
            str: Value of the property, or None if not found.
        """
        property_value = os.environ.get(property_name)
        if not property_value:
            logging.warning(f"The environment variable: {property_name} was not set.")
        return os.environ.get(property_name)

    @classmethod
    def base_url(cls) -> str:
        return cls._get_property('BASE_URL')

    @classmethod
    def browser(cls) -> str | None:
        return cls._get_property('BROWSER')

    @classmethod
    def headless(cls) -> bool:
        return cls._get_property('HEADLESS') is not None and cls._get_property('HEADLESS').lower() == 'true'
