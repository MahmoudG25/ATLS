import json
from django.db import transaction
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.users.models import User
from apps.farm.models import LocationNode, EnclosureProfile
from apps.reports.models import DailyTaskReport, OperationLog, LaborEntry, Operation, Season, Variety, Unit
from apps.production.models import HarvestReport, SortingReport
from apps.accounting.models import Expense, Revenue, Salary
from apps.warehouse.models import Warehouse, Item, Movement
from apps.equipment.models import Equipment, Maintenance, Usage, OilChangeLog
from apps.hr.models import Worker

@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def admin_data_management_view(request):
    """
    Super Admin Control Panel API for bulk data deletion and JSON injections.
    Enforces strict company-tenant isolation constraints for all updates.
    """
    # Enforce SUPER_ADMIN or OWNER permission
    if request.user.role not in ["SUPER_ADMIN", "OWNER"] and not request.user.is_superuser:
        return Response(
            {"error": "غير مصرح لك بالوصول لهذه الخدمة. يجب أن تكون مدير النظام أو المالك."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    company = request.user.company
    
    if request.method == "DELETE":
        module = request.data.get("module")
        if not module:
            return Response({"error": "يرجى تحديد القسم المطلوب حذفه."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                if module == "farm":
                    # Cascade delete related entries to bypass foreign key protection errors safely
                    DailyTaskReport.objects.filter(company=company).delete()
                    HarvestReport.objects.filter(company=company).delete()
                    Movement.objects.filter(company=company).delete()
                    EnclosureProfile.objects.filter(company=company).delete()
                    
                    # Delete all location nodes safely
                    LocationNode.objects.filter(company=company).delete()
                    message = "تم حذف الهيكل التنظيمي للمزرعة بالكامل مع جميع السجلات والتقارير المرتبطة به بنجاح."
                    
                elif module == "users":
                    # Delete users of the company excluding the active super admin/owner
                    deleted_count, _ = User.objects.filter(company=company).exclude(id=request.user.id).delete()
                    message = f"تم حذف جميع مستخدمي الشركة بنجاح (عدد الحذف: {deleted_count} مستخدم)."
                    
                elif module == "hr":
                    # Delete workers
                    Worker.objects.filter(company=company).delete()
                    # Delete engineers from users list (except the current user)
                    deleted_engineers, _ = User.objects.filter(company=company, role="ENGINEER").exclude(id=request.user.id).delete()
                    message = f"تم حذف جميع العمال والمهندسين للشركة بنجاح (حذف {deleted_engineers} مهندس)."

                elif module == "reports":
                    LaborEntry.objects.filter(company=company).delete()
                    OperationLog.objects.filter(company=company).delete()
                    SortingReport.objects.filter(company=company).delete()
                    HarvestReport.objects.filter(company=company).delete()
                    DailyTaskReport.objects.filter(company=company).delete()
                    message = "تم حذف جميع التقارير اليومية، تقارير الحصاد، عمليات الفرز، وسجلات العمالة بنجاح."
                    
                elif module == "finance":
                    Revenue.objects.filter(company=company).delete()
                    Expense.objects.filter(company=company).delete()
                    Salary.objects.filter(company=company).delete()
                    message = "تم حذف جميع الحسابات، الإيرادات، المصروفات، والرواتب بنجاح."
                    
                elif module == "warehouse":
                    Movement.objects.filter(company=company).delete()
                    Item.objects.filter(company=company).delete()
                    Warehouse.objects.filter(company=company).delete()
                    message = "تم حذف جميع المستودعات، الأنشطة المخزنية، وحركات التوريد والصرف بنجاح."
                    
                elif module == "equipment":
                    OilChangeLog.objects.filter(company=company).delete()
                    Maintenance.objects.filter(company=company).delete()
                    Usage.objects.filter(company=company).delete()
                    Equipment.objects.filter(company=company).delete()
                    message = "تم حذف جميع المعدات والآلات، سجلات الصيانة، وسجلات تغيير الزيت، وساعات التشغيل بنجاح."
                    
                else:
                    return Response({"error": "القسم المحدد غير معروف."}, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({"success": True, "message": message})
        except Exception as e:
            return Response({"error": f"حدث خطأ أثناء الحذف: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    elif request.method == "POST":
        module = request.data.get("module")
        data = request.data.get("data")
        
        if not module or data is None:
            return Response({"error": "يرجى تحديد القسم وإرسال البيانات بصيغة JSON."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse data if sent as string
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                return Response({"error": "تنسيق JSON غير صالح."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(data, list):
            return Response({"error": "يجب أن تكون البيانات قائمة (List/Array) من السجلات."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            with transaction.atomic():
                injected_count = 0
                
                if module == "farm":
                    for item in data:
                        name = item.get("name")
                        node_type = item.get("type", "FIELD")
                        parent_name = item.get("parent_name")
                        
                        if not name:
                            return Response({"error": "الاسم حقل مطلوب لكل عقدة في الهيكل."}, status=status.HTTP_400_BAD_REQUEST)
                        
                        parent = None
                        if parent_name:
                            parent = LocationNode.objects.filter(company=company, name=parent_name).first()
                            if not parent:
                                return Response({"error": f"لم يتم العثور على العقدة الأب المذكورة: '{parent_name}'"}, status=status.HTTP_400_BAD_REQUEST)
                        
                        node, created = LocationNode.objects.get_or_create(
                            company=company,
                            name=name,
                            defaults={
                                "type": node_type,
                                "parent": parent
                            }
                        )
                        
                        if node_type == "ENCLOSURE":
                            area = item.get("area_hectares", 10.0)
                            tree_count = item.get("tree_count", 300)
                            EnclosureProfile.objects.update_or_create(
                                company=company,
                                enclosure=node,
                                defaults={
                                    "area_hectares": area,
                                    "tree_count": tree_count
                                }
                            )
                        injected_count += 1
                        
                elif module == "users":
                    for item in data:
                        email = item.get("email")
                        name = item.get("name")
                        role = item.get("role", "ENGINEER")
                        password = item.get("password", "atls123456")
                        
                        if not email or not name:
                            return Response({"error": "البريد الإلكتروني والاسم حقلان مطلوبان لكل مستخدم."}, status=status.HTTP_400_BAD_REQUEST)
                            
                        if User.objects.filter(email=email).exists():
                            continue
                            
                        User.objects.create(
                            email=email,
                            name=name,
                            role=role,
                            password=make_password(password),
                            company=company,
                            is_active=True
                        )
                        injected_count += 1

                elif module == "hr":
                    for item in data:
                        email = item.get("email")
                        # If email is provided, treat it as an Engineer (User)
                        if email:
                            name = item.get("name")
                            password = item.get("password", "atls123456")
                            if not name:
                                return Response({"error": "اسم المهندس حقل مطلوب عند إرسال البريد الإلكتروني."}, status=status.HTTP_400_BAD_REQUEST)
                            
                            if not User.objects.filter(email=email).exists():
                                User.objects.create(
                                    email=email,
                                    name=name,
                                    role="ENGINEER",
                                    password=make_password(password),
                                    company=company,
                                    is_active=True,
                                    is_approved=True
                                )
                                injected_count += 1
                        else:
                            # Treat as Worker
                            name = item.get("name")
                            worker_type = item.get("worker_type", "COMPANY")
                            badge_number = item.get("badge_number", "")
                            national_id = item.get("national_id", "")
                            address = item.get("address", "")
                            monthly_salary = item.get("monthly_salary", 0.0)
                            standard_work_hours = item.get("standard_work_hours", 8)
                            status_val = item.get("status", "active")
                            
                            if not name:
                                return Response({"error": "اسم العامل حقل مطلوب."}, status=status.HTTP_400_BAD_REQUEST)
                                
                            Worker.objects.create(
                                company=company,
                                name=name,
                                worker_type=worker_type,
                                badge_number=badge_number,
                                national_id=national_id,
                                address=address,
                                monthly_salary=monthly_salary,
                                standard_work_hours=standard_work_hours,
                                status=status_val
                            )
                            injected_count += 1
                        
                elif module == "reports":
                    for item in data:
                        report_date = item.get("report_date")
                        loc_name = item.get("location_name")
                        var_name = item.get("variety_name", "مجدول")
                        eng_email = item.get("engineer_email", request.user.email)
                        comp_w = item.get("company_workers", 0)
                        cont_w = item.get("contractor_workers", 0)
                        
                        if not report_date or not loc_name:
                            return Response({"error": "تاريخ التقرير واسم الموقع حقول مطلوبة."}, status=status.HTTP_400_BAD_REQUEST)
                        
                        location = LocationNode.objects.filter(company=company, name=loc_name).first()
                        if not location:
                            return Response({"error": f"الموقع '{loc_name}' غير موجود في الهيكل التنظيمي للشركة."}, status=status.HTTP_400_BAD_REQUEST)
                            
                        variety, _ = Variety.objects.get_or_create(company=company, name=var_name)
                        engineer = User.objects.filter(company=company, email=eng_email).first() or request.user
                        
                        report = DailyTaskReport.objects.create(
                            company=company,
                            report_date=report_date,
                            location=location,
                            variety=variety,
                            engineer=engineer,
                            company_workers=comp_w,
                            contractor_workers=cont_w,
                            status="approved"
                        )
                        
                        logs_data = item.get("logs", [])
                        for log_item in logs_data:
                            op_name = log_item.get("operation_name")
                            prod = log_item.get("actual_productivity", 0.0)
                            notes = log_item.get("notes", "")
                            
                            if not op_name:
                                return Response({"error": "اسم العملية حقل مطلوب داخل سجل الأنشطة."}, status=status.HTTP_400_BAD_REQUEST)
                            
                            operation, _ = Operation.objects.get_or_create(company=company, name=op_name)
                            
                            OperationLog.objects.create(
                                company=company,
                                report=report,
                                operation=operation,
                                actual_productivity=prod,
                                notes=notes,
                                source_id=None
                            )
                        injected_count += 1
                        
                elif module == "finance":
                    for item in data:
                        tx_type = item.get("type", "EXPENSE")
                        amount = item.get("amount", 0.0)
                        date = item.get("date")
                        notes = item.get("notes", "")
                        
                        if not date:
                            return Response({"error": "تاريخ المعاملة المالية مطلوب."}, status=status.HTTP_400_BAD_REQUEST)
                        
                        if tx_type == "REVENUE":
                            Revenue.objects.create(
                                company=company,
                                amount=amount,
                                date=date,
                                notes=notes
                            )
                        elif tx_type == "SALARY":
                            Salary.objects.create(
                                company=company,
                                amount=amount,
                                date=date,
                                notes=notes
                            )
                        else:
                            cat = item.get("category", "other")
                            Expense.objects.create(
                                company=company,
                                amount=amount,
                                category=cat,
                                date=date,
                                notes=notes
                            )
                        injected_count += 1
                        
                elif module == "warehouse":
                    for item in data:
                        w_name = item.get("warehouse_name")
                        w_loc = item.get("location", "")
                        
                        if not w_name:
                            return Response({"error": "اسم المستودع مطلوب."}, status=status.HTTP_400_BAD_REQUEST)
                        
                        warehouse, _ = Warehouse.objects.get_or_create(
                            company=company,
                            name=w_name,
                            defaults={"location": w_loc}
                        )
                        
                        i_name = item.get("item_name")
                        if i_name:
                            cat = item.get("category", "other")
                            qty = item.get("quantity", 0.0)
                            unit = item.get("unit", "")
                            
                            Item.objects.create(
                                company=company,
                                name=i_name,
                                category=cat,
                                quantity=qty,
                                unit=unit,
                                warehouse=warehouse,
                                is_active=True
                            )
                        injected_count += 1
                        
                elif module == "equipment":
                    for item in data:
                        name = item.get("name")
                        if not name:
                            return Response({"error": "اسم المعدة مطلوب."}, status=status.HTTP_400_BAD_REQUEST)
                        
                        eq_type = item.get("type", "TRACTOR")
                        model_num = item.get("model", "")
                        serial = item.get("serial_number", "")
                        status_val = item.get("status", "active")
                        spec = item.get("specifications", {})
                        curr_hrs = item.get("current_hours", 0.0)
                        interval_hrs = item.get("oil_change_interval_hours", 250.0)
                        interval_days = item.get("oil_change_interval_days", 180)
                        
                        equipment, _ = Equipment.objects.get_or_create(
                            company=company,
                            name=name,
                            defaults={
                                "type": eq_type,
                                "model": model_num,
                                "serial_number": serial,
                                "status": status_val,
                                "specifications": spec,
                                "current_hours": curr_hrs,
                                "oil_change_interval_hours": interval_hrs,
                                "oil_change_interval_days": interval_days,
                            }
                        )
                        
                        # Maintenances
                        m_list = item.get("maintenances", [])
                        for m_item in m_list:
                            m_date = m_item.get("date")
                            m_notes = m_item.get("notes", "")
                            m_cost = m_item.get("cost", 0.0)
                            if m_date:
                                Maintenance.objects.create(
                                    company=company,
                                    equipment=equipment,
                                    date=m_date,
                                    notes=m_notes,
                                    cost=m_cost,
                                )
                            
                        # Usages
                        u_list = item.get("usages", [])
                        for u_item in u_list:
                            u_date = u_item.get("date")
                            hours = u_item.get("hours_used", 0.0)
                            fuel = u_item.get("fuel_consumption")
                            if u_date:
                                Usage.objects.create(
                                    company=company,
                                    equipment=equipment,
                                    date=u_date,
                                    hours_used=hours,
                                    fuel_consumption=fuel
                                )
                                # Update running hours
                                equipment.current_hours += hours
                                equipment.save()
                                
                        injected_count += 1
                else:
                    return Response({"error": "القسم المحدد غير معروف."}, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({
                    "success": True,
                    "message": f"تم بنجاح حقن عدد {injected_count} سجل في قسم '{module}'."
                })
        except Exception as e:
            return Response({"error": f"حدث خطأ أثناء حقن البيانات: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
