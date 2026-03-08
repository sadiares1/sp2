from django.apps import apps
from django.db.models.signals import post_delete, post_save


def _get_compiled_model():
    return apps.get_model("core", "CompiledCharacteristic")


def _upsert_compiled(sender, instance):
    if sender.__name__ == "CompiledCharacteristic":
        return

    compiled_model = _get_compiled_model()
    passport_data = getattr(instance, "passportData", None)
    crop_name = None
    if passport_data and getattr(passport_data, "crop", None):
        crop_name = passport_data.crop.crop_name

    compiled_model.objects.update_or_create(
        source_model=sender.__name__,
        source_id=instance.pk,
        defaults={
            "passportData": passport_data,
            "crop_name": crop_name,
        },
    )


def _delete_compiled(sender, instance):
    if sender.__name__ == "CompiledCharacteristic":
        return

    compiled_model = _get_compiled_model()
    compiled_model.objects.filter(
        source_model=sender.__name__,
        source_id=instance.pk,
    ).delete()


def _post_save_handler(sender, instance, **kwargs):
    _upsert_compiled(sender, instance)


def _post_delete_handler(sender, instance, **kwargs):
    _delete_compiled(sender, instance)


def connect_characteristics_signals():
    app_config = apps.get_app_config("core")
    for model in app_config.get_models():
        model_name = model.__name__
        if not model_name.endswith("Characteristics"):
            continue
        if model_name == "CompiledCharacteristic":
            continue

        post_save.connect(_post_save_handler, sender=model, weak=False)
        post_delete.connect(_post_delete_handler, sender=model, weak=False)
