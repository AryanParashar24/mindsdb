import gitlab

from mindsdb.integrations.handlers.gitlab_handler.gitlab_tables import GitlabIssuesTable
from mindsdb.integrations.libs.api_handler import APIHandler
from mindsdb.integrations.libs.response import (
    HandlerStatusResponse as StatusResponse,
)

from mindsdb.utilities.log import get_log
from mindsdb_sql import parse_sql

logger = get_log("integrations.gitlab_handler")


class GitlabHandler(APIHandler):
    """The GitLab handler implementation"""

    def __init__(self, name: str, **kwargs):
        """ constructor
        Args:
            name (str): the handler name
        """
        super().__init__(name)

        connection_data = kwargs.get("connection_data", {})
        self.connection_data = connection_data
        self.repository = connection_data["repository"]
        self.kwargs = kwargs

        self.connection = None
        self.is_connected = False

        gitlab_issues_data = GitlabIssuesTable(self)
        self._register_table("issues", gitlab_issues_data)

    def connect(self) -> StatusResponse:
        """ Set up the connections required by the handler
        Returns:
            HandlerStatusResponse
        """

        connection_kwargs = {}

        if self.connection_data.get("api_key", None):
            connection_kwargs["private_token"] = self.connection_data["api_key"]

        self.connection = gitlab.Gitlab(**connection_kwargs)
        self.is_connected = True

        return self.connection

    def check_connection(self) -> StatusResponse:
        """Check connection to the handler
        Returns:
            HandlerStatusResponse
        """
        response = StatusResponse(False)

        try:
            self.connect()
            if self.connection_data.get("api_key", None):
                logger.info(f"Authenticated as user")
            else:
                logger.info("Proceeding without an API key")

            response.success = True
        except Exception as e:
            logger.error(f"Error connecting to GitLab API: {e}!")
            response.error_message = e

        self.is_connected = response.success

        return response

    def native_query(self, query: str) -> StatusResponse:
        """Receive and process raw query.
        Args:
            query (str): query in a native format
        Returns:
            HandlerResponse
        """
        ast = parse_sql(query, dialect="mindsdb")
        return self.query(ast)
