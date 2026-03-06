import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_photo_passport_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='AkapulkoCharacteristics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('growth_habit', models.TextField(blank=True, null=True)),
                ('branching_habit', models.TextField(blank=True, null=True)),
                ('plant_height_aboveground_m', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('plant_span_spread_m', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('internode_length_cm', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('stem_diameter_base_cm', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('leaflet_shape', models.TextField(blank=True, null=True)),
                ('leaflet_apex', models.TextField(blank=True, null=True)),
                ('leaf_color_rhs', models.TextField(blank=True, null=True)),
                ('leaf_length_cm', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('leaf_width_cm', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('leaf_length_width_ratio', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('leaflet_length_cm', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('leaflet_width_cm', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('leaflet_length_width_ratio', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('petiole_color_rhs', models.TextField(blank=True, null=True)),
                ('petiole_width_cm', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('date_of_first_flowering', models.DateField(blank=True, null=True)),
                ('flower_color_rhs', models.TextField(blank=True, null=True)),
                ('infloresence_position', models.TextField(blank=True, null=True)),
                ('bract_size', models.TextField(blank=True, null=True)),
                ('pod_color', models.TextField(blank=True, null=True)),
                ('pod_length_cm', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('pod_size_variability', models.TextField(blank=True, null=True)),
                ('pod_ridge', models.TextField(blank=True, null=True)),
                ('pod_luster_dark_stage', models.TextField(blank=True, null=True)),
                ('ease_of_seed_extraction', models.TextField(blank=True, null=True)),
                ('seed_color_rhs', models.TextField(blank=True, null=True)),
                ('seed_surface', models.TextField(blank=True, null=True)),
                ('seed_length_mm', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('seed_width_mm', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('hundred_seed_weight_g', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='akapulko_characteristics/')),
                ('notes', models.TextField(blank=True, null=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('passportData', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='akapulko_characteristics', to='core.passportdata')),
            ],
        ),
    ]
