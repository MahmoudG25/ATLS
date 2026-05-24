from django.core.management.base import BaseCommand
from apps.farm.models import Farm, Crop, Stage, Enclosure


class Command(BaseCommand):
    help = "Seeds the database with the farm hierarchy (Palm/Olive) and their stages/enclosures."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Starting farm structure seeding..."))

        # 1. Ensure the Farm exists
        farm, created = Farm.objects.get_or_create(
            name="Atlas Farm", defaults={"is_active": True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created Farm: {farm.name}"))

        # 2. Create Crops
        palm_crop, created = Crop.objects.get_or_create(
            farm=farm, name="نخيل", defaults={"type": "palm", "order": 1}
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created Crop: Palm"))

        olive_crop, created = Crop.objects.get_or_create(
            farm=farm, name="زيتون", defaults={"type": "olive", "order": 2}
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created Crop: Olive"))

        # 3. Create Palm Stages and Enclosures
        palm_structure = [
            {
                "name": "المرحلة 1",
                "enclosures": [str(i) for i in range(1, 8) if i != 6],
            },  # 1->7 exclude 6
            {
                "name": "المرحلة 2",
                "enclosures": [str(i) for i in range(6, 21) if i != 7],
            },  # 6->20 exclude 7
            {
                "name": "المرحلة 3",
                "enclosures": [str(i) for i in range(21, 33)],
            },  # 21->32
            {"name": "المرحلة 4", "enclosures": [str(i) for i in range(1, 7)]},  # 1->6
            {"name": "المرحلة 5", "enclosures": [str(i) for i in range(7, 10)]},  # 7->9
            {"name": "المرحلة 6", "enclosures": ["10", "11"]},  # 10, 11
            {
                "name": "المرحلة 7",
                "enclosures": [str(i) for i in range(12, 16)],
            },  # 12->15
            {"name": "المرحلة 8", "enclosures": ["مجمعه 66 فدان"]},
            {"name": "المرحلة 9", "enclosures": ["جديدة"]},
            {"name": "المرحلة 10", "enclosures": ["جديدة"]},
            {"name": "الصوبة", "enclosures": []},  # treated as special stage
        ]

        for idx, stage_data in enumerate(palm_structure, start=1):
            stage, created = Stage.objects.get_or_create(
                crop=palm_crop, name=stage_data["name"], defaults={"order": idx}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created Stage: {idx}"))

            for enc_idx, enc_name in enumerate(stage_data["enclosures"], start=1):
                enc, enc_created = Enclosure.objects.get_or_create(
                    crop=palm_crop,
                    stage=stage,
                    name=enc_name,
                    defaults={"order": enc_idx},
                )
                if enc_created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"    Created Enclosure: {enc_idx} for Stage {idx}"
                        )
                    )

        # 4. Create Olive Regions (Directly linked to Crop)
        olive_regions = ["منطقة الفنجان", "منطقة الجركن", "منطقة 26", "منطقة الساحل"]

        for idx, region_name in enumerate(olive_regions, start=1):
            enc, enc_created = Enclosure.objects.get_or_create(
                crop=olive_crop, stage=None, name=region_name, defaults={"order": idx}
            )
            if enc_created:
                self.stdout.write(
                    self.style.SUCCESS(f"  Created Olive Region (Enclosure): {idx}")
                )

        self.stdout.write(
            self.style.SUCCESS("Farm structure seeding completed successfully!")
        )
