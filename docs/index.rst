Tableau Server Client
=====================

.. autosummary::
   :toctree: api

   tableauserverclient.Server
   tableauserverclient.Pager

Authentication
--------------

.. autosummary::
   :toctree: api

   tableauserverclient.TableauAuth
   tableauserverclient.PersonalAccessTokenAuth
   tableauserverclient.JWTAuth

Content models
--------------

.. autosummary::
   :toctree: api

   tableauserverclient.WorkbookItem
   tableauserverclient.DatasourceItem
   tableauserverclient.ViewItem
   tableauserverclient.FlowItem
   tableauserverclient.MetricItem
   tableauserverclient.ProjectItem
   tableauserverclient.CustomViewItem
   tableauserverclient.VirtualConnectionItem

User and group models
---------------------

.. autosummary::
   :toctree: api

   tableauserverclient.UserItem
   tableauserverclient.GroupItem
   tableauserverclient.GroupSetItem

Scheduling and jobs
-------------------

.. autosummary::
   :toctree: api

   tableauserverclient.ScheduleItem
   tableauserverclient.JobItem
   tableauserverclient.BackgroundJobItem
   tableauserverclient.TaskItem
   tableauserverclient.FlowRunItem
   tableauserverclient.LinkedTaskItem
   tableauserverclient.LinkedTaskStepItem
   tableauserverclient.LinkedTaskFlowRunItem
   tableauserverclient.IntervalItem
   tableauserverclient.HourlyInterval
   tableauserverclient.DailyInterval
   tableauserverclient.WeeklyInterval
   tableauserverclient.MonthlyInterval

Site and server
---------------

.. autosummary::
   :toctree: api

   tableauserverclient.SiteItem
   tableauserverclient.SiteAuthConfiguration
   tableauserverclient.SiteOIDCConfiguration
   tableauserverclient.ServerInfoItem
   tableauserverclient.RevisionItem

Permissions and subscriptions
------------------------------

.. autosummary::
   :toctree: api

   tableauserverclient.Permission
   tableauserverclient.PermissionsRule
   tableauserverclient.SubscriptionItem
   tableauserverclient.FavoriteItem

Data management
---------------

.. autosummary::
   :toctree: api

   tableauserverclient.DatabaseItem
   tableauserverclient.TableItem
   tableauserverclient.ColumnItem
   tableauserverclient.ConnectionItem
   tableauserverclient.ConnectionCredentials
   tableauserverclient.DQWItem
   tableauserverclient.DataFreshnessPolicyItem
   tableauserverclient.DataAlertItem

Webhooks and extensions
-----------------------

.. autosummary::
   :toctree: api

   tableauserverclient.WebhookItem
   tableauserverclient.ExtensionsServer
   tableauserverclient.ExtensionsSiteSettings
   tableauserverclient.SafeExtension

Querying and filtering
----------------------

.. autosummary::
   :toctree: api

   tableauserverclient.RequestOptions
   tableauserverclient.CSVRequestOptions
   tableauserverclient.ExcelRequestOptions
   tableauserverclient.ImageRequestOptions
   tableauserverclient.PDFRequestOptions
   tableauserverclient.PPTXRequestOptions
   tableauserverclient.Filter
   tableauserverclient.Sort

Errors
------

.. autosummary::
   :toctree: api

   tableauserverclient.ServerResponseError
   tableauserverclient.MissingRequiredFieldError
   tableauserverclient.FailedSignInError
   tableauserverclient.NotSignedInError
