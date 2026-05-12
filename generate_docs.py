import os
from datetime import datetime

base_dir = "docs_v2"

structure = {
    "00_PROJECT_CORE": [
        "PRODUCT_VISION.md", "SYSTEM_PHILOSOPHY.md", "BUSINESS_GOALS.md", "PLATFORM_DIRECTION.md"
    ],
    "01_ARCHITECTURE": [
        "DOMAIN_DRIVEN_ARCHITECTURE.md", "FRONTEND_ARCHITECTURE.md", "BACKEND_ARCHITECTURE.md", 
        "DATABASE_ARCHITECTURE.md", "API_ARCHITECTURE.md", "EVENT_SYSTEM.md", 
        "MEDIA_ARCHITECTURE.md", "STATE_MANAGEMENT.md", "OFFLINE_STRATEGY.md"
    ],
    "02_UI_UX": [
        "DESIGN_SYSTEM.md", "MOBILE_FIRST_STRATEGY.md", "RTL_SYSTEM.md", "NAVIGATION_SYSTEM.md", 
        "DASHBOARD_SYSTEM.md", "THEME_ENGINE.md", "COMPONENT_GUIDELINES.md", "UX_PATTERNS.md"
    ],
    "03_DOMAINS": [
        "FARM_DOMAIN.md", "OPERATIONS_DOMAIN.md", "HARVEST_DOMAIN.md", "INVENTORY_DOMAIN.md", 
        "HR_DOMAIN.md", "EQUIPMENT_DOMAIN.md", "ANALYTICS_DOMAIN.md", "REPORTING_DOMAIN.md", 
        "MEDIA_DOMAIN.md", "AUDIT_DOMAIN.md", "NOTIFICATION_DOMAIN.md"
    ],
    "04_DYNAMIC_ENGINES": [
        "DYNAMIC_FORM_ENGINE.md", "DYNAMIC_HIERARCHY_ENGINE.md", "DYNAMIC_THEME_ENGINE.md", 
        "ROLE_PERMISSION_ENGINE.md", "DASHBOARD_CONFIGURATION_ENGINE.md", "CONFIGURATION_ENGINE.md"
    ],
    "05_FRONTEND": [
        "FOLDER_STRUCTURE.md", "ROUTING_SYSTEM.md", "SHADCN_GUIDE.md", "TAILWIND_RULES.md", 
        "COMPONENT_ARCHITECTURE.md", "PWA_STRATEGY.md", "FORM_PATTERNS.md", "ANIMATION_SYSTEM.md"
    ],
    "06_BACKEND": [
        "DJANGO_STRUCTURE.md", "DJANGO_SERVICES_LAYER.md", "SERIALIZER_RULES.md", "QUERY_RULES.md", 
        "FILE_STORAGE_SYSTEM.md", "SEASON_SYSTEM.md", "BACKUP_SYSTEM.md", "SECURITY_RULES.md"
    ],
    "07_AI_AGENT": [
        "AI_DEVELOPMENT_RULES.md", "AI_CODE_STYLE_GUIDE.md", "AI_WORKFLOW.md", "AI_FORBIDDEN_ACTIONS.md", 
        "AI_TASK_TEMPLATE.md", "AI_PROGRESS_UPDATE_RULES.md", "PROMPT_LIBRARY.md"
    ],
    "08_EXECUTION": [
        "MASTER_ROADMAP.md", "PHASE_01.md", "PHASE_02.md", "PHASE_03.md", "CURRENT_PROGRESS.md", 
        "TECH_DEBT.md", "CHANGELOG.md"
    ],
    "09_REFERENCE": [
        "API_REFERENCE.md", "DATABASE_REFERENCE.md", "ROLE_MATRIX.md", "DESIGN_TOKENS.md", 
        "OPERATION_TYPES.md", "CROP_TYPES.md", "GLOSSARY.md"
    ]
}

template = """# {title}

## Purpose
Short explanation of the document purpose.

## Scope
What this document covers.

## Current Status
- [ ] Not Started
- [ ] In Progress
- [ ] Completed

## Planned Sections
- [ ] Section 1
- [ ] Section 2
- [ ] Section 3

## Dependencies
List related docs.

## Notes
Important notes placeholder.

## Last Updated
{date}
"""

today = datetime.now().strftime("%Y-%m-%d")

os.makedirs(base_dir, exist_ok=True)

for folder, files in structure.items():
    folder_path = os.path.join(base_dir, folder)
    os.makedirs(folder_path, exist_ok=True)
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        title = filename.replace(".md", "").replace("_", " ")
        content = template.format(title=title, date=today)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

print("Documentation structure generated successfully.")
