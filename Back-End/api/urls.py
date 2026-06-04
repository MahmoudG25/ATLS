from django.urls import path, include
from api.endpoints import auth_views
from api.endpoints import farm_views
from api.endpoints import palm_views
from api.endpoints import olive_views
from api.endpoints import warehouse_views
from api.endpoints.warehouse_views import items_view, movements_view, item_detail_view
from api.endpoints import equipment_views
from api.endpoints import accounting_views
from api.endpoints import production_views
from api.endpoints import reports_views
from api.endpoints.reports_views import (
    CostAnalyticsView,
    TrendsAnalyticsView,
    InsightsAnalyticsView,
)
from api.endpoints import hr_views
from api.endpoints import upload_views
from api.endpoints import notification_views
from api.endpoints import activity_views
from api.endpoints import admin_data_views

urlpatterns = [
    path("admin/config/", admin_data_views.FarmSystemConfigView.as_view(), name="farm-config"),
    path("admin/data-management", admin_data_views.admin_data_management_view, name="admin_data_management"),
    path("auth/activity-logs", activity_views.activity_log_view, name="activity_logs"),
    path("auth/register", auth_views.register_view, name="register"),
    path("auth/login", auth_views.login_view, name="login"),
    path("auth/me", auth_views.me_view, name="me"),
    path("auth/me/security", auth_views.change_password_view, name="me_security"),
    path("auth/password-reset/request", auth_views.password_reset_request_view, name="password_reset_request"),
    path("auth/password-reset/status", auth_views.password_reset_status_view, name="password_reset_status"),
    path("auth/password-reset/confirm", auth_views.password_reset_confirm_view, name="password_reset_confirm"),
    path("auth/admin/password-resets", auth_views.admin_password_resets_list_view, name="admin_password_resets"),
    path("auth/admin/password-resets/<uuid:id>/<str:action>", auth_views.admin_password_reset_action_view, name="admin_password_reset_action"),
    path("auth/public/landing", auth_views.landing_content_view, name="public_landing"),
    # Admin User Managment
    path("users", auth_views.users_collection_view, name="users_collection"),
    path("auth/permissions", auth_views.get_app_permissions_view, name="app_permissions"),
    path("auth/debug-permissions", auth_views.debug_permissions_view, name="debug_permissions"),
    path("users/<uuid:id>/permissions", auth_views.user_permissions_view, name="user_permissions"),
    path("users/engineers", auth_views.engineers_list_view, name="users_engineers"),
    path("users/<uuid:id>/approve", auth_views.approve_user_view, name="approve_user"),
    path(
        "users/<uuid:id>/deactivate",
        auth_views.deactivate_user_view,
        name="deactivate_user",
    ),
    path(
        "users/<uuid:id>/role", auth_views.update_user_role_view, name="update_user_role"
    ),
    path("users/<uuid:id>/delete", auth_views.delete_user_view, name="delete_user"),
    path("users/<uuid:id>/reset-avatar", auth_views.reset_user_avatar_view, name="reset_user_avatar"),

    # Admin CMS Mappings
    path(
        "admin/landing-content",
        auth_views.manage_landing_content_view,
        name="manage_landing",
    ),
    # Announcements — Bulletin Board
    path("announcements/", auth_views.announcements_view, name="announcements_list"),
    path("announcements/<int:pk>/", auth_views.announcement_detail_view, name="announcement_detail"),
    # Farm Structure Mappings
    path("farm/farms", farm_views.farms_list_view, name="farms_list"),
    path("farm/location-tree/", farm_views.location_tree_view, name="location_tree"),
    path("farm/settings/", farm_views.farm_settings_view, name="farm_settings"),
    path("farm/location-nodes/", farm_views.location_nodes_view, name="location_nodes"),
    path(
        "farm/location-nodes/<str:pk>/",
        farm_views.location_node_detail_view,
        name="location_node_detail",
    ),
    path(
        "farm/location-nodes/<str:pk>/profile/",
        farm_views.location_node_profile_view,
        name="location_node_profile",
    ),
    path(
        "farm/location-nodes/<str:pk>/timeline/",
        farm_views.LocationNodeTimelineView.as_view(),
        name="location_node_timeline",
    ),
    path(
        "farm/location-nodes/<str:pk>/analytics/",
        farm_views.location_node_analytics_view,
        name="location_node_analytics",
    ),
    # Palm Mappings
    path("palm/records", palm_views.palm_collection_view, name="palm_collection"),
    path("palm/records/<str:id>", palm_views.palm_detail_view, name="palm_detail"),
    # Olive Mappings
    path("olive/records", olive_views.olive_collection_view, name="olive_collection"),
    path("olive/records/<str:id>", olive_views.olive_detail_view, name="olive_detail"),
    # Warehouse Mappings
    path("warehouse/warehouses/", warehouse_views.WarehouseListCreateView.as_view(), name="warehouse-list"),
    path("warehouse/warehouses/<str:pk>/", warehouse_views.WarehouseDetailView.as_view(), name="warehouse-detail"),
    path("warehouse/items/", items_view, name="warehouse-items"),
    path("warehouse/items/<str:pk>/", item_detail_view, name="warehouse-item-detail"),
    path("warehouse/movements/", movements_view, name="warehouse-movements"),
    path("warehouse/alerts/", warehouse_views.MaterialAlertFeedView.as_view(), name="warehouse-alerts-feed"),
    path("warehouse/alerts/<uuid:pk>/resolve/", warehouse_views.MaterialAlertResolveView.as_view(), name="warehouse-alerts-resolve"),
    # Equipment Mappings
    path("equipment/", equipment_views.equipment_list_create_api, name="equipment_list_create_api"),
    path("equipment/logs/", equipment_views.equipment_logs_create_api, name="equipment_logs_create_api"),
    path("equipment/alerts/", equipment_views.equipment_alerts_list_api, name="equipment_alerts_list_api"),
    path("equipment/alerts/<uuid:pk>/resolve/", equipment_views.equipment_alerts_resolve_api, name="equipment_alerts_resolve_api"),
    path("equipment/profile/<uuid:pk>/", equipment_views.equipment_profile_detail_api, name="equipment_profile_detail_api"),
    path("equipment/<uuid:pk>/", equipment_views.equipment_detail_api, name="equipment_detail_api"),
    
    path("equipment/list", equipment_views.equipment_list_view, name="equipment_list"),
    path(
        "equipment/oil-changes",
        equipment_views.oil_change_view,
        name="equipment_oil_changes",
    ),
    path(
        "equipment/oil-alerts",
        equipment_views.oil_alerts_view,
        name="equipment_oil_alerts",
    ),
    path(
        "equipment/<str:id>",
        equipment_views.equipment_detail_view,
        name="equipment_detail",
    ),
    path(
        "equipment/maintenance",
        equipment_views.maintenance_view,
        name="equipment_maintenance",
    ),
    path("equipment/usage", equipment_views.usage_view, name="equipment_usage"),
    # Accounting Mappings
    path(
        "accounting/summary",
        accounting_views.finance_summary_view,
        name="finance_summary",
    ),
    path("accounting/expenses", accounting_views.expenses_view, name="expenses"),
    path("accounting/revenues", accounting_views.revenues_view, name="revenues"),
    path("accounting/salaries", accounting_views.salaries_view, name="salaries"),
    path("accounting/invoices", accounting_views.invoices_view, name="invoices"),
    path("accounting/invoices/<uuid:id>", accounting_views.invoice_detail_view, name="invoice_detail"),
    # Production Mappings
    path("production/", include("apps.production.urls")),
    # Reports Mappings
    path(
        "reports/tasks/",
        reports_views.DailyTaskReportListCreate.as_view(),
        name="reports_tasks",
    ),
    path(
        "reports/media-feed/",
        reports_views.MediaFeedView.as_view(),
        name="reports_media_feed",
    ),
    path(
        "reports/tasks/<str:pk>/",
        reports_views.DailyTaskReportDetail.as_view(),
        name="reports_tasks_detail",
    ),
    path(
        "reports/tasks/<str:pk>/<str:action>/",
        reports_views.DailyTaskReportActionView.as_view(),
        name="reports_tasks_action",
    ),
    path(
        "reports/tasks/summary/",
        reports_views.DailyTaskSummaryView.as_view(),
        name="reports_tasks_summary",
    ),
    path(
        "reports/tasks/export/",
        reports_views.DailyTaskExportView.as_view(),
        name="reports_tasks_export",
    ),
    path(
        "reports/analytics/operations/",
        reports_views.OperationAnalyticsView.as_view(),
        name="reports_analytics_operations",
    ),
    path(
        "reports/analytics/workers/",
        reports_views.WorkerAnalyticsView.as_view(),
        name="reports_analytics_workers",
    ),
    path("analytics/costs/", CostAnalyticsView.as_view()),
    path("analytics/trends/", TrendsAnalyticsView.as_view()),
    path(
        "analytics/kpi/", reports_views.KPIAnalyticsView.as_view(), name="analytics_kpi"
    ),
    path(
        "analytics/productivity/",
        reports_views.ProductivityAnalyticsView.as_view(),
        name="analytics_productivity",
    ),
    path(
        "analytics/operations-summary/",
        reports_views.OperationsSummaryView.as_view(),
        name="analytics_operations_summary",
    ),
    path(
        "analytics/workers-by-location/",
        reports_views.WorkersByLocationView.as_view(),
        name="analytics_workers_by_location",
    ),
    path(
        "analytics/operation-location-matrix/",
        reports_views.OperationLocationMatrixView.as_view(),
        name="analytics_operation_location_matrix",
    ),
    path(
        "analytics/comparison/",
        reports_views.ComparisonAnalyticsView.as_view(),
        name="analytics_comparison",
    ),
    path(
        "analytics/dashboard/",
        reports_views.DashboardAnalyticsView.as_view(),
        name="analytics_dashboard",
    ),
    path("analytics/insights/", InsightsAnalyticsView.as_view()),
    path(
        "reports/fertilization/",
        reports_views.FertilizationListCreate.as_view(),
        name="reports_fertilization",
    ),
    path(
        "reports/fertilization/<str:pk>/",
        reports_views.FertilizationDetail.as_view(),
        name="reports_fertilization_detail",
    ),
    path(
        "reports/irrigation/",
        reports_views.IrrigationListCreate.as_view(),
        name="reports_irrigation",
    ),
    path(
        "reports/irrigation/<str:pk>/",
        reports_views.IrrigationDetail.as_view(),
        name="reports_irrigation_detail",
    ),
    path(
        "reports/pest-control/",
        reports_views.PestControlListCreate.as_view(),
        name="reports_pest_control",
    ),
    path(
        "reports/pest-control/<str:pk>/",
        reports_views.PestControlDetail.as_view(),
        name="reports_pest_control_detail",
    ),
    path(
        "reports/allocations/",
        reports_views.OperationalLocationAllocationListCreate.as_view(),
        name="reports_allocations",
    ),
    path(
        "reports/allocations/<str:pk>/",
        reports_views.OperationalLocationAllocationDetail.as_view(),
        name="reports_allocations_detail",
    ),
    path(
        "reports/operations/",
        reports_views.OperationListView.as_view(),
        name="reports_operations",
    ),
    path(
        "reports/operations/<str:pk>/",
        reports_views.OperationDetailView.as_view(),
        name="reports_operations_detail",
    ),
    path(
        "reports/options/",
        reports_views.ReportDropdownOptionListCreate.as_view(),
        name="reports_options_list",
    ),
    path(
        "reports/options/<str:pk>/",
        reports_views.ReportDropdownOptionDetail.as_view(),
        name="reports_options_detail",
    ),
    path(
        "reports/varieties/",
        reports_views.VarietyListView.as_view(),
        name="reports_varieties",
    ),
    path(
        "reports/varieties/<str:pk>/",
        reports_views.VarietyDetailView.as_view(),
        name="reports_varieties_detail",
    ),
    path("reports/units/", reports_views.UnitListView.as_view(), name="reports_units"),
    path("reports/units/<str:pk>/", reports_views.UnitDetailView.as_view(), name="reports_units_detail"),
    path("reports/application-methods/", reports_views.ApplicationMethodListView.as_view(), name="reports_application_methods"),
    path("reports/application-methods/<str:pk>/", reports_views.ApplicationMethodDetailView.as_view(), name="reports_application_methods_detail"),
    path("reports/seasons/", reports_views.SeasonListView.as_view(), name="reports_seasons"),
    path(
        "reports/contractors/",
        reports_views.ContractorListView.as_view(),
        name="reports_contractors",
    ),
    path(
        "reports/contractors/<str:pk>/",
        reports_views.ContractorDetailView.as_view(),
        name="reports_contractors_detail",
    ),
    path(
        "reports/custom-fields/",
        reports_views.CustomFieldDefinitionListCreate.as_view(),
        name="custom_fields_list",
    ),
    path(
        "reports/custom-fields/<str:pk>/",
        reports_views.CustomFieldDefinitionDetail.as_view(),
        name="custom_fields_detail",
    ),
    path(
        "reports/custom-field-values/",
        reports_views.CustomFieldValueListCreate.as_view(),
        name="custom_field_values_list",
    ),
    path(
        "reports/custom-field-values/<str:pk>/",
        reports_views.CustomFieldValueDetail.as_view(),
        name="custom_field_values_detail",
    ),
    path(
        "reports/labor/",
        reports_views.LaborEntryListCreate.as_view(),
        name="reports_labor_list",
    ),
    path(
        "reports/attachments/",
        reports_views.AttachmentListCreate.as_view(),
        name="reports_attachments_list",
    ),
    path(
        "reports/attachments/<str:pk>/",
        reports_views.AttachmentDetail.as_view(),
        name="reports_attachments_detail",
    ),

    path(
        "reports/gallery/",
        reports_views.GalleryMediaListCreate.as_view(),
        name="reports_gallery_list",
    ),
    path(
        "reports/gallery/<str:pk>/",
        reports_views.GalleryMediaDetail.as_view(),
        name="reports_gallery_detail",
    ),
    path("uploads/", upload_views.UploadFileView.as_view(), name="upload_file"),
    
    # HR Mappings
    path("hr/workers/", hr_views.WorkerListCreateView.as_view(), name="hr_workers_list"),
    path("hr/workers/<uuid:pk>/", hr_views.WorkerDetailView.as_view(), name="hr_worker_detail"),
    path("hr/periods/", hr_views.PayrollPeriodListCreateView.as_view(), name="hr_periods"),
    path("hr/transactions/", hr_views.PayrollTransactionListView.as_view(), name="hr_transactions"),
    path("hr/transactions/<uuid:pk>/", hr_views.PayrollTransactionDetailView.as_view(), name="hr_transaction_detail"),
    path("hr/transactions/bulk-approve/", hr_views.BulkApproveTransactionsView.as_view(), name="hr_transactions_bulk_approve"),
    path("hr/reviews/", hr_views.PendingWorkerReviewListView.as_view(), name="hr_worker_reviews"),
    path("hr/reviews/<uuid:pk>/resolve/", hr_views.ResolvePendingWorkerReviewView.as_view(), name="hr_worker_review_resolve"),
    path("hr/contractors/ledger/", hr_views.ContractorLedgerListView.as_view(), name="hr_contractor_ledger"),
    path("hr/contractors/ledger/create/", hr_views.ContractorLedgerCreateView.as_view(), name="hr_contractor_ledger_create"),
    path("hr/contractors/<uuid:contractor_id>/dashboard/", hr_views.ContractorDashboardView.as_view(), name="hr_contractor_dashboard"),

    # HR Staff, Document, and Payroll Components Mappings
    path("hr/employees/", hr_views.EmployeeListView.as_view(), name="hr_employees_list"),
    path("hr/employees/me/", hr_views.EmployeeMeView.as_view(), name="hr_employee_me"),
    path("hr/employees/<uuid:pk>/", hr_views.EmployeeDetailView.as_view(), name="hr_employee_detail"),
    path("hr/available-users/", hr_views.AvailableUsersListView.as_view(), name="hr_available_users"),
    path("hr/documents/", hr_views.EmployeeDocumentListCreateView.as_view(), name="hr_documents_list"),
    path("hr/documents/<uuid:pk>/verify/", hr_views.EmployeeDocumentVerifyView.as_view(), name="hr_document_verify"),
    path("hr/payroll-components/", hr_views.PayrollComponentListCreateView.as_view(), name="hr_payroll_components_list"),
    path("hr/payroll-components/<uuid:pk>/", hr_views.PayrollComponentDetailView.as_view(), name="hr_payroll_component_detail"),
    
    # HR Leave Requests Mappings
    path("hr/leaves/", hr_views.LeaveRequestListCreateView.as_view(), name="hr_leaves_list"),
    path("hr/leaves/<uuid:pk>/", hr_views.LeaveRequestDetailView.as_view(), name="hr_leave_detail"),
    path("hr/leaves/<uuid:pk>/approve/", hr_views.LeaveRequestReviewView.as_view(), name="hr_leave_approve"),

    # Notification Mappings
    path(
        "notifications/",
        notification_views.notifications_list_view,
        name="notifications_list",
    ),
    path(
        "notifications/<str:id>/read/",
        notification_views.notification_read_view,
        name="notification_read",
    ),
    path(
        "notifications/read-all/",
        notification_views.notifications_read_all_view,
        name="notifications_read_all",
    ),
]
