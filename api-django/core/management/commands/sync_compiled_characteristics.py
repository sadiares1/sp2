from django.apps import apps
from django.core.management.base import BaseCommand

from core.models import CompiledCharacteristic


class Command(BaseCommand):
    help = "Rebuild CompiledCharacteristic rows from all *Characteristics models."

    def handle(self, *args, **options):
        app_config = apps.get_app_config("core")

        characteristic_models = [
            model
            for model in app_config.get_models()
            if model.__name__.endswith("Characteristics") and model.__name__ != "CompiledCharacteristic"
        ]

        existing_keys = set()
        created_count = 0
        updated_count = 0

        for model in characteristic_models:
            queryset = model.objects.select_related("passportData", "passportData__crop").all()
            for instance in queryset:
                source_key = (model.__name__, instance.pk)
                existing_keys.add(source_key)

                passport_data = getattr(instance, "passportData", None)
                crop_name = None
                if passport_data and getattr(passport_data, "crop", None):
                    crop_name = passport_data.crop.crop_name

                _, created = CompiledCharacteristic.objects.update_or_create(
                    source_model=model.__name__,
                    source_id=instance.pk,
                    defaults={
                        "passportData": passport_data,
                        "crop_name": crop_name,
                    },
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        deleted_count, _ = CompiledCharacteristic.objects.exclude(
            source_model__in=[model.__name__ for model in characteristic_models]
        ).delete()

        stale_qs = CompiledCharacteristic.objects.all()
        stale_ids = [
            item.id
            for item in stale_qs
            if (item.source_model, item.source_id) not in existing_keys
        ]
        if stale_ids:
            CompiledCharacteristic.objects.filter(id__in=stale_ids).delete()
            deleted_count += len(stale_ids)

        self.stdout.write(
            self.style.SUCCESS(
                f"Compiled characteristics synced. Created: {created_count}, Updated: {updated_count}, Deleted: {deleted_count}"
            )
        )