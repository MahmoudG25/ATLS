import re
from django.core.management.base import BaseCommand
from apps.reports.models import ReportDropdownOption, Contractor, Unit, Variety, Operation

def normalize_arabic(text):
    if not text:
        return ""
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[أإآ]', 'ا', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'[\u064B-\u065F]', '', text) # Remove diacritics
    return text

class Command(BaseCommand):
    help = "Rescues orphaned legacy ReportDropdownOption records into normalized master data tables."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Scan and print intended actions without writing to DB.')

    def safe_print(self, msg, style_func=None):
        if style_func:
            msg = style_func(msg)
        try:
            self.stdout.write(msg)
        except UnicodeEncodeError:
            self.stdout.write(msg.encode('ascii', 'replace').decode('ascii'))

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.safe_print(f"Starting Rescue Master Data (Dry Run: {dry_run})", self.style.WARNING)
        
        legacy_options = ReportDropdownOption.objects.filter(category__in=['contractor', 'unit', 'variety', 'operation'])
        
        stats = {
            'total_scanned': legacy_options.count(),
            'rescued': 0,
            'skipped_exact': 0,
            'skipped_normalized': 0,
            'ambiguous': 0,
            'failed': 0
        }

        for option in legacy_options:
            try:
                norm_name = normalize_arabic(option.name)
                company = option.company
                if not company:
                    from apps.users.models import Company
                    company = Company.objects.first()
                    self.safe_print(f"[ORPHAN RESCUE] Option '{option.name}' had no company. Assigned to: {company}", self.style.WARNING)
                
                # Model mappings
                if option.category == 'contractor':
                    TargetModel = Contractor
                elif option.category == 'unit':
                    TargetModel = Unit
                elif option.category == 'variety':
                    TargetModel = Variety
                elif option.category == 'operation':
                    TargetModel = Operation
                else:
                    continue
                    
                target_qs = TargetModel.objects.filter(company=company)
                
                # Idempotency / Exact match
                exact_matches = target_qs.filter(name=option.name)
                if exact_matches.exists():
                    stats['skipped_exact'] += 1
                    continue
                    
                # Normalized match
                normalized_matches = []
                for t in target_qs:
                    if normalize_arabic(t.name) == norm_name:
                        normalized_matches.append(t)
                        
                if len(normalized_matches) == 1:
                    stats['skipped_normalized'] += 1
                    self.safe_print(f"[SKIP NORM] '{option.name}' semantically matches '{normalized_matches[0].name}'")
                    continue
                    
                elif len(normalized_matches) > 1:
                    stats['ambiguous'] += 1
                    self.safe_print(f"[AMBIGUOUS] '{option.name}' matches multiple existing targets: {[t.name for t in normalized_matches]}", self.style.WARNING)
                    continue
                    
                # Rescue
                stats['rescued'] += 1
                
                # Snapshot backup
                import json
                import datetime
                import os
                
                snapshot = {
                    'legacy_id': option.id,
                    'category': option.category,
                    'original_name': option.name,
                    'normalized_name': norm_name,
                    'company_id': getattr(company, 'id', None),
                    'rescued_at': datetime.datetime.now().isoformat()
                }
                
                snapshot_dir = os.path.join('apps', 'reports', 'management', 'commands')
                with open(os.path.join(snapshot_dir, 'rescue_snapshot_log.jsonl'), 'a', encoding='utf-8') as f:
                    f.write(json.dumps(snapshot, ensure_ascii=False) + '\n')
                
                if not dry_run:
                    defaults = {}
                    if hasattr(TargetModel, 'is_active'):
                        defaults['is_active'] = option.is_active
                    if option.category == 'contractor':
                        defaults['rate_per_hour'] = 0
                    TargetModel.objects.create(company=company, name=option.name, **defaults)
                
                self.safe_print(f"[{'WOULD RESCUE' if dry_run else 'RESCUED'}] {option.category}: '{option.name}' (Company: {company})", self.style.SUCCESS)

            except Exception as e:
                stats['failed'] += 1
                self.safe_print(f"[FAILED] ID {option.id}: {str(e)}", self.style.ERROR)

        # Print Summary
        self.safe_print("\n=== RESCUE SUMMARY ===", self.style.MIGRATE_HEADING)
        self.safe_print(f"Dry Run: {dry_run}")
        for k, v in stats.items():
            self.safe_print(f"{k.upper()}: {v}")
