from django.urls import path
from api.endpoints import auth_views
from api.endpoints import farm_views
from api.endpoints.farm_views import sector_detail_view, plot_detail_view
from api.endpoints import palm_views
from api.endpoints import olive_views
from api.endpoints import warehouse_views
from api.endpoints.warehouse_views import items_view, movements_view, item_detail_view
from api.endpoints import equipment_views
from api.endpoints import accounting_views
from api.endpoints import production_views
from api.endpoints import reports_views
from api.endpoints import notification_views
from api.endpoints import activity_views

urlpatterns = [
    path('auth/activity-logs', activity_views.activity_log_view, name='activity_logs'),
    path('auth/register', auth_views.register_view, name='register'),
    path('auth/login', auth_views.login_view, name='login'),
    path('auth/me', auth_views.me_view, name='me'),
    path('auth/me/security', auth_views.change_password_view, name='me_security'),
    path('auth/public/landing', auth_views.landing_content_view, name='public_landing'),
    
    # Admin User Managment
    path('users', auth_views.users_collection_view, name='users_collection'),
    path('users/<int:id>/approve', auth_views.approve_user_view, name='approve_user'),
    path('users/<int:id>/deactivate', auth_views.deactivate_user_view, name='deactivate_user'),
    path('users/<int:id>/role', auth_views.update_user_role_view, name='update_user_role'),
    path('users/<int:id>/delete', auth_views.delete_user_view, name='delete_user'),

    # Admin CMS Mappings
    path('admin/landing-content', auth_views.manage_landing_content_view, name='manage_landing'),

    # Farm Structure Mappings
    path('farm/farms', farm_views.farms_list_view, name='farms_list'),
    path('farm/croptypes', farm_views.croptypes_list_view, name='croptypes_list'),
    path('farm/structure', farm_views.structure_view, name='structure'),
    path('farm/hierarchy', farm_views.hierarchy_view, name='hierarchy'),
    path('farm/sectors', farm_views.create_sector_view, name='create_sector'),
    path('farm/sectors/<int:pk>/', sector_detail_view, name='sector_detail'),
    path('farm/plots', farm_views.create_plot_view, name='create_plot'),
    path('farm/plots/<int:pk>/', plot_detail_view, name='plot_detail'),
    path('farm/plots/<int:id>/stats', farm_views.plot_stats_view, name='plot_stats'),
    
    # Palm Mappings
    path('palm/records', palm_views.palm_collection_view, name='palm_collection'),
    path('palm/records/<int:id>', palm_views.palm_detail_view, name='palm_detail'),

    # Olive Mappings
    path('olive/records', olive_views.olive_collection_view, name='olive_collection'),
    path('olive/records/<int:id>', olive_views.olive_detail_view, name='olive_detail'),

    # Warehouse Mappings
    path('warehouse/items/', items_view, name='warehouse-items'),
    path('warehouse/items/<int:pk>/', item_detail_view, name='warehouse-item-detail'),
    path('warehouse/movements/', movements_view, name='warehouse-movements'),

    # Equipment Mappings
    path('equipment/list', equipment_views.equipment_list_view, name='equipment_list'),
    path('equipment/<int:id>', equipment_views.equipment_detail_view, name='equipment_detail'),
    path('equipment/maintenance', equipment_views.maintenance_view, name='equipment_maintenance'),
    path('equipment/usage', equipment_views.usage_view, name='equipment_usage'),

    # Accounting Mappings
    path('accounting/summary', accounting_views.finance_summary_view, name='finance_summary'),
    path('accounting/expenses', accounting_views.expenses_view, name='expenses'),
    path('accounting/revenues', accounting_views.revenues_view, name='revenues'),
    path('accounting/salaries', accounting_views.salaries_view, name='salaries'),

    # Production Mappings
    path('production/yields', production_views.yield_view, name='production_yields'),

    # Reports Mappings
    path('reports/tasks/', reports_views.DailyTaskReportListCreate.as_view(), name='reports_tasks'),
    path('reports/tasks/<int:pk>/', reports_views.DailyTaskReportDetail.as_view(), name='reports_tasks_detail'),
    path('reports/tasks/summary/', reports_views.DailyTaskSummaryView.as_view(), name='reports_tasks_summary'),
    path('reports/tasks/export/', reports_views.DailyTaskExportView.as_view(), name='reports_tasks_export'),
    path('reports/fertilization/', reports_views.FertilizationListCreate.as_view(), name='reports_fertilization'),
    path('reports/fertilization/<int:pk>/', reports_views.FertilizationDetail.as_view(), name='reports_fertilization_detail'),
    path('reports/irrigation/', reports_views.IrrigationListCreate.as_view(), name='reports_irrigation'),
    path('reports/irrigation/<int:pk>/', reports_views.IrrigationDetail.as_view(), name='reports_irrigation_detail'),
    path('reports/operations/', reports_views.OperationListView.as_view(), name='reports_operations'),
    path('reports/options/', reports_views.ReportDropdownOptionListCreate.as_view(), name='reports_options_list'),
    path('reports/options/<int:pk>/', reports_views.ReportDropdownOptionDetail.as_view(), name='reports_options_detail'),

    path('reports/custom-fields/', reports_views.CustomFieldDefinitionListCreate.as_view(), name='custom_fields_list'),
    path('reports/custom-fields/<int:pk>/', reports_views.CustomFieldDefinitionDetail.as_view(), name='custom_fields_detail'),
    path('reports/custom-field-values/', reports_views.CustomFieldValueListCreate.as_view(), name='custom_field_values_list'),
    path('reports/custom-field-values/<int:pk>/', reports_views.CustomFieldValueDetail.as_view(), name='custom_field_values_detail'),

    # Notification Mappings
    path('notifications/', notification_views.notifications_list_view, name='notifications_list'),
    path('notifications/<int:id>/read/', notification_views.notification_read_view, name='notification_read'),
    path('notifications/read-all/', notification_views.notifications_read_all_view, name='notifications_read_all'),
]
