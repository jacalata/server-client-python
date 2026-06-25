"""
E2E tests for Publisher-level operations against a real Tableau server.

Requires: TABLEAU_SERVER, TABLEAU_SITE, TABLEAU_TOKEN, TABLEAU_TOKEN_NAME
Optional:  TABLEAU_PROJECT (defaults to "Default")

Run with:
    pytest test_e2e/test_publisher.py -v -m e2e
"""
import os
from pathlib import Path

import pytest
import tableauserverclient as TSC
from tableauserverclient.models import Resource

ASSETS_DIR = Path(__file__).parent / "assets"
SAMPLE_WORKBOOK = ASSETS_DIR / "WorkbookWithoutExtract.twbx"
EXTRACT_WORKBOOK = ASSETS_DIR / "WorkbookWithExtract.twbx"
SAMPLE_DATASOURCE = ASSETS_DIR / "WorldIndicators.tdsx"

pytestmark = pytest.mark.e2e


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def workbook(server, project_id):
    """Publish a workbook for this module's tests, clean up after."""
    wb = TSC.WorkbookItem(name="tsc-e2e-publisher-wb", project_id=project_id)
    wb = server.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    yield wb
    server.workbooks.delete(wb.id)


# ---------------------------------------------------------------------------
# Workbook CRUD
# ---------------------------------------------------------------------------


def test_workbook_publish_and_get(server, project_id):
    """Published workbook is retrievable by id and has correct name/project."""
    wb = TSC.WorkbookItem(name="tsc-e2e-publish-test", project_id=project_id)
    wb = server.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    try:
        fetched = server.workbooks.get_by_id(wb.id)
        assert fetched.id == wb.id
        assert fetched.name == "tsc-e2e-publish-test"
        assert fetched.project_id == project_id
    finally:
        server.workbooks.delete(wb.id)


def test_workbook_update(server, workbook):
    """Updating a workbook's name and description persists on the server."""
    original_name = workbook.name
    workbook.name = "tsc-e2e-publisher-wb-renamed"
    workbook.description = "updated by e2e test"
    updated = server.workbooks.update(workbook)
    try:
        assert updated.name == "tsc-e2e-publisher-wb-renamed"
        assert updated.description == "updated by e2e test"
    finally:
        workbook.name = original_name
        workbook.description = ""
        server.workbooks.update(workbook)


def test_workbook_download(server, workbook, tmp_path):
    """Downloaded workbook file exists and is non-empty."""
    path = server.workbooks.download(workbook.id, str(tmp_path))
    assert Path(path).exists()
    assert Path(path).stat().st_size > 0


def test_workbook_populate_views(server, workbook):
    """populate_views returns at least one view for the test workbook."""
    server.workbooks.populate_views(workbook)
    assert workbook.views is not None
    assert len(workbook.views) > 0


def test_workbook_populate_connections(server, workbook):
    """populate_connections returns a list (may be empty for extract-only wb)."""
    server.workbooks.populate_connections(workbook)
    assert workbook.connections is not None


def test_workbook_preview_image(server, workbook):
    """populate_preview_image succeeds without error (image may be empty for freshly-published workbooks)."""
    server.workbooks.populate_preview_image(workbook)
    assert workbook.preview_image is not None


def test_workbook_tags(server, workbook):
    """Tags added to a workbook round-trip correctly and can be removed."""
    server.workbooks.add_tags(workbook, ["e2e-tag-a", "e2e-tag-b"])
    fetched = server.workbooks.get_by_id(workbook.id)
    try:
        assert "e2e-tag-a" in fetched.tags
        assert "e2e-tag-b" in fetched.tags
    finally:
        server.workbooks.delete_tags(workbook, ["e2e-tag-a", "e2e-tag-b"])
    fetched = server.workbooks.get_by_id(workbook.id)
    assert "e2e-tag-a" not in fetched.tags


# ---------------------------------------------------------------------------
# View exports
# ---------------------------------------------------------------------------


def test_view_export_png(server, workbook, tmp_path):
    """A view can be exported as a PNG image."""
    server.workbooks.populate_views(workbook)
    view = workbook.views[0]
    server.views.populate_image(view)
    assert view.image is not None
    assert len(view.image) > 0


def test_view_export_pdf(server, workbook, tmp_path):
    """A view can be exported as a PDF."""
    server.workbooks.populate_views(workbook)
    view = workbook.views[0]
    opts = TSC.PDFRequestOptions()
    server.views.populate_pdf(view, opts)
    assert view.pdf is not None
    assert len(view.pdf) > 0


def test_view_export_csv(server, workbook):
    """A view can be exported as CSV data."""
    server.workbooks.populate_views(workbook)
    view = workbook.views[0]
    server.views.populate_csv(view)
    assert view.csv is not None


# ---------------------------------------------------------------------------
# Datasource CRUD
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def extract_workbook(server, project_id):
    """Publish a workbook with an extract for refresh/extract tests, clean up after."""
    wb = TSC.WorkbookItem(name="tsc-e2e-extract-wb", project_id=project_id)
    wb = server.workbooks.publish(wb, EXTRACT_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    yield wb
    server.workbooks.delete(wb.id)


@pytest.fixture(scope="module")
def datasource(server, project_id):
    """Publish a datasource for this module's tests, clean up after."""
    ds = TSC.DatasourceItem(project_id=project_id, name="tsc-e2e-publisher-ds")
    ds = server.datasources.publish(ds, str(SAMPLE_DATASOURCE), TSC.Server.PublishMode.Overwrite)
    yield ds
    server.datasources.delete(ds.id)


def test_datasource_publish_and_get(server, datasource):
    """Published datasource is retrievable by id."""
    fetched = server.datasources.get_by_id(datasource.id)
    assert fetched.id == datasource.id
    assert fetched.name == "tsc-e2e-publisher-ds"


def test_datasource_update(server, datasource):
    """Updating datasource description persists."""
    datasource.description = "updated by e2e test"
    updated = server.datasources.update(datasource)
    assert updated.description == "updated by e2e test"


def test_datasource_download(server, datasource, tmp_path):
    """Downloaded datasource file exists and is non-empty."""
    path = server.datasources.download(datasource.id, str(tmp_path))
    assert Path(path).exists()
    assert Path(path).stat().st_size > 0


def test_datasource_populate_connections(server, datasource):
    """populate_connections returns a list for a published datasource."""
    server.datasources.populate_connections(datasource)
    assert datasource.connections is not None


def test_datasource_tags(server, datasource):
    """Tags added to a datasource round-trip correctly."""
    server.datasources.add_tags(datasource, ["e2e-ds-tag"])
    fetched = server.datasources.get_by_id(datasource.id)
    try:
        assert "e2e-ds-tag" in fetched.tags
    finally:
        server.datasources.delete_tags(datasource, ["e2e-ds-tag"])


# ---------------------------------------------------------------------------
# Favorites
# ---------------------------------------------------------------------------


def test_favorites_workbook(server, workbook):
    """A workbook can be added to and removed from favorites."""
    user = TSC.UserItem()
    user.id = server.user_id
    server.favorites.add_favorite(user, Resource.Workbook, workbook)
    server.favorites.get(user)
    assert any(f.id == workbook.id for f in user.favorites.get("workbooks", []))
    server.favorites.delete_favorite_workbook(user, workbook)


def test_favorites_view(server, workbook):
    """A view can be added to and removed from favorites."""
    server.workbooks.populate_views(workbook)
    view = workbook.views[0]
    user = TSC.UserItem()
    user.id = server.user_id
    server.favorites.add_favorite_view(user, view)
    server.favorites.get(user)
    assert any(f.id == view.id for f in user.favorites.get("views", []))
    server.favorites.delete_favorite_view(user, view)


def test_favorites_datasource(server, datasource):
    """A datasource can be added to and removed from favorites."""
    user = TSC.UserItem()
    user.id = server.user_id
    server.favorites.add_favorite_datasource(user, datasource)
    server.favorites.get(user)
    assert any(f.id == datasource.id for f in user.favorites.get("datasources", []))
    server.favorites.delete_favorite_datasource(user, datasource)


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------


def test_pager_workbooks(server):
    """Pager iterates over all workbooks without error."""
    count = sum(1 for _ in TSC.Pager(server.workbooks))
    assert count >= 0


def test_queryset_filter(server):
    """QuerySet filter returns only matching workbooks."""
    results = list(server.workbooks.filter(name="tsc-e2e-publisher-wb"))
    assert all(wb.name == "tsc-e2e-publisher-wb" for wb in results)


# ---------------------------------------------------------------------------
# Workbook refresh and extract
# ---------------------------------------------------------------------------


def test_workbook_refresh(server, extract_workbook):
    """Triggering a workbook refresh returns a job item."""
    job = server.workbooks.refresh(extract_workbook)
    assert job.id is not None


def test_workbook_create_and_delete_extract(server, extract_workbook):
    """An extract can be deleted from a workbook and then recreated.

    Requires a workbook asset whose datasource is supported on the target server OS.
    WorkbookWithExtract.twbx uses MS Access which fails on Linux servers -- replace
    the asset with a compatible .twbx to enable this test.
    """
    pytest.skip("WorkbookWithExtract.twbx uses MS Access (not supported on Linux) -- replace asset to enable")


# ---------------------------------------------------------------------------
# Datasource refresh
# ---------------------------------------------------------------------------


def test_datasource_refresh(server, datasource):
    """Triggering a datasource refresh returns a job item."""
    job = server.datasources.refresh(datasource)
    assert job.id is not None


# ---------------------------------------------------------------------------
# Metadata API
# ---------------------------------------------------------------------------


def test_metadata_query(server):
    """Metadata GraphQL API returns a valid response structure."""
    result = server.metadata.query(
        """
        {
            publishedDatasourcesConnection(first: 5) {
                nodes {
                    luid
                    name
                }
            }
        }
        """
    )
    assert "data" in result
    assert "publishedDatasourcesConnection" in result["data"]


