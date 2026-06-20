"""
E2E tests for SiteAdmin-level operations against a real Tableau server.

All tests in this file are marked with @pytest.mark.site_admin and are skipped
unless TABLEAU_IS_ADMIN=1 (or "true"/"yes") is set in the environment. The token
configured in TABLEAU_TOKEN must belong to an account with SiteAdminCreator
or SiteAdminExplorer role.

Run with:
    TABLEAU_IS_ADMIN=1 pytest test_e2e/test_site_admin.py -v -m e2e
"""
from datetime import time
from pathlib import Path

import pytest
import tableauserverclient as TSC

ASSETS_DIR = Path(__file__).parent / "assets"
SAMPLE_WORKBOOK = ASSETS_DIR / "WorkbookWithoutExtract.twbx"
SAMPLE_DATASOURCE = ASSETS_DIR / "WorldIndicators.tdsx"

pytestmark = [pytest.mark.e2e, pytest.mark.site_admin]


# ---------------------------------------------------------------------------
# Jobs (requires admin)
# ---------------------------------------------------------------------------


def test_jobs_get(server):
    """jobs.get() returns a list without error."""
    jobs, _ = server.jobs.get()
    assert isinstance(jobs, list)


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------


def test_project_create_update_delete(server, project_id):
    """A project can be created, updated, and deleted."""
    project = TSC.ProjectItem(name="tsc-e2e-admin-project", description="created by e2e test")
    project = server.projects.create(project)
    try:
        assert project.id is not None
        fetched = server.projects.filter(name="tsc-e2e-admin-project")[0]
        assert fetched.id == project.id

        project.description = "updated by e2e test"
        updated = server.projects.update(project)
        assert updated.description == "updated by e2e test"
    finally:
        server.projects.delete(project.id)


def test_nested_project(server):
    """A nested (child) project can be created under a parent."""
    parent = TSC.ProjectItem(name="tsc-e2e-parent-project")
    parent = server.projects.create(parent)
    try:
        child = TSC.ProjectItem(name="tsc-e2e-child-project", parent_id=parent.id)
        child = server.projects.create(child)
        try:
            assert child.parent_id == parent.id
        finally:
            server.projects.delete(child.id)
    finally:
        server.projects.delete(parent.id)


def test_project_workbook_default_permissions(server):
    """Workbook default permissions on a project can be updated and queried."""
    project = TSC.ProjectItem(name="tsc-e2e-perm-project")
    project = server.projects.create(project)
    try:
        server.projects.populate_workbook_default_permissions(project)
        assert project.default_workbook_permissions is not None
    finally:
        server.projects.delete(project.id)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


def test_user_add_and_remove(server):
    """A user can be added to the site and removed."""
    user = TSC.UserItem("tsc-e2e-testuser", "Unlicensed")
    user = server.users.add(user)
    try:
        assert user.id is not None
        fetched = server.users.get_by_id(user.id)
        assert fetched.name == "tsc-e2e-testuser"
    finally:
        server.users.remove(user.id)


# ---------------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def group(server):
    """Create a group for group tests, clean up after."""
    g = TSC.GroupItem("tsc-e2e-admin-group")
    g = server.groups.create(g)
    yield g
    server.groups.delete(g.id)


def test_group_create_and_get(server, group):
    """Created group appears in the group list."""
    results = list(server.groups.filter(name="tsc-e2e-admin-group"))
    assert any(g.id == group.id for g in results)


def test_group_add_and_remove_user(server, group):
    """A user can be added to and removed from a group."""
    user = TSC.UserItem("tsc-e2e-group-user", "Unlicensed")
    user = server.users.add(user)
    try:
        server.groups.add_user(group, user.id)
        server.groups.populate_users(group)
        assert any(u.id == user.id for u in group.users)

        server.groups.remove_user(group, user.id)
        server.groups.populate_users(group)
        assert all(u.id != user.id for u in group.users)
    finally:
        server.users.remove(user.id)


# ---------------------------------------------------------------------------
# Schedules
# ---------------------------------------------------------------------------


def test_schedule_create_and_delete(server):
    """An extract schedule can be created and deleted."""
    interval = TSC.HourlyInterval(start_time=time(3, 0), end_time=time(23, 0), interval_value=4)
    schedule = TSC.ScheduleItem(
        "tsc-e2e-hourly-schedule",
        50,
        TSC.ScheduleItem.Type.Extract,
        TSC.ScheduleItem.ExecutionOrder.Parallel,
        interval,
    )
    schedule = server.schedules.create(schedule)
    try:
        assert schedule.id is not None
        fetched = server.schedules.get_by_id(schedule.id)
        assert fetched.name == "tsc-e2e-hourly-schedule"
    finally:
        server.schedules.delete(schedule.id)


def test_schedule_add_workbook(server, project_id):
    """A workbook can be added to an extract refresh schedule."""
    interval = TSC.DailyInterval(start_time=time(4, 0))
    schedule = TSC.ScheduleItem(
        "tsc-e2e-daily-schedule",
        60,
        TSC.ScheduleItem.Type.Extract,
        TSC.ScheduleItem.ExecutionOrder.Serial,
        interval,
    )
    schedule = server.schedules.create(schedule)
    wb = TSC.WorkbookItem(name="tsc-e2e-schedule-wb", project_id=project_id)
    wb = server.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    try:
        server.schedules.add_to_schedule(schedule.id, wb)
        tasks, _ = server.tasks.get()
        assert any(getattr(t, "schedule_id", None) == schedule.id for t in tasks)
    finally:
        server.workbooks.delete(wb.id)
        server.schedules.delete(schedule.id)


# ---------------------------------------------------------------------------
# Webhooks
# ---------------------------------------------------------------------------


def test_webhook_create_and_delete(server):
    """A webhook can be created and deleted."""
    webhook = TSC.WebhookItem()
    webhook.name = "tsc-e2e-webhook"
    webhook.url = "https://example.com/tsc-e2e-webhook"
    webhook.event = "datasource-created"
    webhook = server.webhooks.create(webhook)
    try:
        assert webhook.id is not None
        all_webhooks, _ = server.webhooks.get()
        assert any(w.id == webhook.id for w in all_webhooks)
    finally:
        server.webhooks.delete(webhook.id)


# ---------------------------------------------------------------------------
# Move workbook between projects
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Connection update
# ---------------------------------------------------------------------------


def test_datasource_update_connection(server, project_id):
    """A datasource connection's embed_password flag can be toggled via update_connection."""
    ds = TSC.DatasourceItem(project_id=project_id, name="tsc-e2e-conn-ds")
    ds = server.datasources.publish(ds, str(SAMPLE_DATASOURCE), TSC.Server.PublishMode.Overwrite)
    try:
        server.datasources.populate_connections(ds)
        if not ds.connections:
            pytest.skip("Published datasource has no connections to update")
        conn = ds.connections[0]
        conn.embed_password = False
        updated_conn = server.datasources.update_connection(ds, conn)
        assert updated_conn is not None
    finally:
        server.datasources.delete(ds.id)


# ---------------------------------------------------------------------------
# Data freshness policy
# ---------------------------------------------------------------------------


def test_workbook_data_freshness_policy(server, project_id):
    """Workbook data freshness policy can be set to AlwaysLive and back to SiteDefault."""
    wb = TSC.WorkbookItem(name="tsc-e2e-freshness-wb", project_id=project_id)
    wb = server.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    try:
        wb.data_freshness_policy = TSC.DataFreshnessPolicyItem(TSC.DataFreshnessPolicyItem.Option.AlwaysLive)
        updated = server.workbooks.update(wb)
        assert updated.data_freshness_policy.option == TSC.DataFreshnessPolicyItem.Option.AlwaysLive

        wb.data_freshness_policy = TSC.DataFreshnessPolicyItem(TSC.DataFreshnessPolicyItem.Option.SiteDefault)
        updated = server.workbooks.update(wb)
        assert updated.data_freshness_policy.option == TSC.DataFreshnessPolicyItem.Option.SiteDefault
    finally:
        server.workbooks.delete(wb.id)


# ---------------------------------------------------------------------------
# Group filter and sort
# ---------------------------------------------------------------------------


def test_group_filter_by_name(server):
    """Groups can be filtered by name using RequestOptions."""
    g = TSC.GroupItem("tsc-e2e-filter-group")
    g = server.groups.create(g)
    try:
        opts = TSC.RequestOptions()
        opts.filter.add(
            TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, "tsc-e2e-filter-group")
        )
        results, _ = server.groups.get(req_options=opts)
        assert len(results) == 1
        assert results[0].id == g.id
    finally:
        server.groups.delete(g.id)


def test_group_filter_queryset(server):
    """Groups can be filtered using the django-style QuerySet interface."""
    g = TSC.GroupItem("tsc-e2e-qs-group")
    g = server.groups.create(g)
    try:
        results = list(server.groups.filter(name="tsc-e2e-qs-group"))
        assert any(r.id == g.id for r in results)
    finally:
        server.groups.delete(g.id)


def test_workbook_move_project(server, project_id):
    """A workbook can be moved from one project to another."""
    dest = TSC.ProjectItem(name="tsc-e2e-dest-project")
    dest = server.projects.create(dest)
    wb = TSC.WorkbookItem(name="tsc-e2e-move-wb", project_id=project_id)
    wb = server.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    try:
        wb.project_id = dest.id
        updated = server.workbooks.update(wb)
        assert updated.project_id == dest.id
    finally:
        server.workbooks.delete(wb.id)
        server.projects.delete(dest.id)
