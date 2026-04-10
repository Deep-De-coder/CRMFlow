from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceAuthenticationFailed
from app.config import get_settings
from app.salesforce.exceptions import SalesforceAuthError
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class SalesforceClient:
    """
    Manages the Salesforce connection lifecycle.
    Wraps simple-salesforce with error handling and
    a singleton connection pattern.
    """

    def __init__(self, settings=None):
        self._settings = settings or get_settings()
        self._sf: Salesforce | None = None

    def connect(self) -> Salesforce:
        """
        Establish connection to Salesforce.
        Returns authenticated Salesforce instance.
        Raises SalesforceAuthError on failure.
        """
        try:
            self._sf = Salesforce(
                username=self._settings.sf_username,
                password=self._settings.sf_password,
                security_token=self._settings.sf_security_token,
                domain=self._settings.sf_domain,
            )
            logger.info("Salesforce connection established.")
            return self._sf
        except SalesforceAuthenticationFailed as e:
            raise SalesforceAuthError(
                f"Salesforce authentication failed: {e}"
            ) from e

    def get_connection(self) -> Salesforce:
        """
        Return existing connection or create a new one.
        """
        if self._sf is None:
            return self.connect()
        return self._sf

    @property
    def sf(self) -> Salesforce:
        return self.get_connection()


@lru_cache
def get_sf_client() -> SalesforceClient:
    return SalesforceClient()
