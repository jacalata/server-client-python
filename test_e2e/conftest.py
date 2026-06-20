import os
import pytest
import tableauserverclient as TSC


def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: mark test as end-to-end (requires a real Tableau server)")
    config.addinivalue_line("markers", "site_admin: mark test as requiring SiteAdmin permissions")


@pytest.fixture(scope="session")
def server():
    """
    Authenticated TSC server session for e2e tests.

    Required environment variables:
        TABLEAU_SERVER     -- server URL, e.g. https://10ax.online.tableau.com
        TABLEAU_SITE       -- site content URL
        TABLEAU_TOKEN      -- personal access token value
        TABLEAU_TOKEN_NAME -- personal access token name

    Optional:
        TABLEAU_IS_ADMIN   -- set to "1" or "true" if the token belongs to a SiteAdmin account.
                              Tests marked with @pytest.mark.site_admin are skipped when not set.
    """
    url = os.environ.get("TABLEAU_SERVER")
    site = os.environ.get("TABLEAU_SITE", "")
    token = os.environ.get("TABLEAU_TOKEN")
    token_name = os.environ.get("TABLEAU_TOKEN_NAME")

    if not all([url, token, token_name]):
        pytest.skip("E2E tests require TABLEAU_SERVER, TABLEAU_TOKEN, and TABLEAU_TOKEN_NAME env vars")

    server = TSC.Server(url, use_server_version=True)
    auth = TSC.PersonalAccessTokenAuth(token_name, token, site)
    with server.auth.sign_in(auth):
        yield server


@pytest.fixture(scope="session")
def is_admin():
    val = os.environ.get("TABLEAU_IS_ADMIN", "").strip().lower()
    return val in ("1", "true", "yes")


def pytest_runtest_setup(item):
    if item.get_closest_marker("site_admin"):
        val = os.environ.get("TABLEAU_IS_ADMIN", "").strip().lower()
        if val not in ("1", "true", "yes"):
            pytest.skip("Skipping site_admin test: set TABLEAU_IS_ADMIN=1 to run")


@pytest.fixture(scope="session")
def project_id(server):
    """Return the ID of the project named by TABLEAU_PROJECT (default 'Default')."""
    project_name = os.environ.get("TABLEAU_PROJECT", "Sandbox")
    opts = TSC.RequestOptions()
    opts.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, project_name))
    projects, _ = server.projects.get(opts)
    if not projects:
        pytest.skip(f"Project {project_name!r} not found -- set TABLEAU_PROJECT env var")
    return projects[0].id
