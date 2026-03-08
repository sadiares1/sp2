from django.http import JsonResponse
from django.core.paginator import Paginator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
import pandas as pd
from core.models import (
    PassportData, Location, Crop, Donor, 
    Topography, Availability, Photo, Usage, CompiledCharacteristic
)

# Constants
CROP_GROUPS = [
    "Cereals", "Vegetables", "Legumes", "Root Crops", "Medicinal Crops",
    "Fruits", "Tree Nuts", "Plantation Crops", "Pasture and Forage", "Ornamentals"
]


def _to_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _normalize_crop_group(value):
    normalized = (value or '').strip().lower()
    if not normalized:
        return None

    allowed_map = {group.lower(): group for group in CROP_GROUPS}
    return allowed_map.get(normalized)


def _serialize_passport_full(passport, request):
    usage_items = [
        {
            'plant_part': usage.plant_part,
            'usage_description': usage.usage_description,
        }
        for usage in passport.usages.all()
    ]

    first_photo = passport.photo
    if first_photo is None:
        first_photo = passport.photos.first()

    photos_data = []
    for photo in passport.photos.all():
        photo_url = None
        if photo.photo:
            try:
                photo_url = request.build_absolute_uri(photo.photo.url)
            except Exception:
                photo_url = None

        photos_data.append(
            {
                'id': photo.id,
                'photo_name': photo.photo_name,
                'url': photo_url,
            }
        )

    return {
        'id': passport.id,
        'collection_country_code': passport.collection_country_code,
        'gb_number': passport.gb_number,
        'accession_number': passport.accession_number,
        'old_accession_number': passport.old_accession_number,
        'collection_number': passport.collection_number,
        'collecting_date': passport.collecting_date.isoformat() if passport.collecting_date else None,
        'acquisition_date': passport.acquisition_date.isoformat() if passport.acquisition_date else None,
        'collector': passport.collector,

        'crop_group': passport.crop.crop_group if passport.crop else None,
        'crop_name': passport.crop.crop_name if passport.crop else None,
        'genus': passport.crop.genus if passport.crop else None,
        'species': passport.crop.species if passport.crop else None,
        'local_name': passport.crop.local_name if passport.crop else None,
        'species_authority': passport.crop.species_authority if passport.crop else None,
        'subtaxon': passport.crop.subtaxon if passport.crop else None,
        'accession_name': passport.crop.accession_name if passport.crop else None,
        'biologicalStatus': passport.crop.biologicalStatus if passport.crop else None,
        'storage': passport.crop.storage if passport.crop else None,
        'samplingMethod': passport.crop.samplingMethod if passport.crop else None,
        'materialCollected': passport.crop.materialCollected if passport.crop else None,
        'sampleType': passport.crop.sampleType if passport.crop else None,

        'country': passport.location.country if passport.location else None,
        'province': passport.location.province if passport.location else None,
        'nearest_town': passport.location.nearest_town if passport.location else None,
        'barangay': passport.location.barangay if passport.location else None,
        'purok_or_sitio': passport.location.purok_or_sitio if passport.location else None,
        'latitude': passport.location.latitude if passport.location else None,
        'longitude': passport.location.longitude if passport.location else None,
        'altitude': passport.location.altitude if passport.location else None,

        'donor_name': passport.donor.donor_name if passport.donor else None,
        'growers_name': passport.donor.growers_name if passport.donor else None,
        'growers_contact_number': passport.donor.growers_contact_number if passport.donor else None,
        'donor_code': passport.donor.donor_code if passport.donor else None,
        'donor_accession_number': passport.donor.donor_accession_number if passport.donor else None,
        'location_duplicate_site': passport.donor.location_duplicate_site if passport.donor else None,
        'duplicate_institution_name': passport.donor.duplicate_institution_name if passport.donor else None,
        'other_donor_code_name': passport.donor.other_donor_code_name if passport.donor else None,

        'site': passport.topography.site if passport.topography else None,
        'topography': passport.topography.topography if passport.topography else None,
        'soil_texture': passport.topography.soil_texture if passport.topography else None,
        'soil_color': passport.topography.soil_color if passport.topography else None,
        'drainage': passport.topography.drainage if passport.topography else None,
        'stoniness': passport.topography.stoniness if passport.topography else None,
        'diseases_and_pests': passport.topography.diseases_and_pests if passport.topography else None,
        'remarks': passport.topography.remarks if passport.topography else None,
        'cultural_practice': passport.topography.cultural_practice if passport.topography else None,
        'herbarium_specimen': passport.topography.herbarium_specimen if passport.topography else None,

        'available_in_the_field': passport.availability.available_in_the_field if passport.availability else None,
        'available_at_in_vitro': passport.availability.available_at_in_vitro if passport.availability else None,
        'available_for_distribution': passport.availability.available_for_distribution if passport.availability else None,
        'status_of_harvest': passport.availability.status_of_harvest if passport.availability else None,
        'characterized': passport.availability.characterized if passport.availability else None,
        'field': passport.availability.field if passport.availability else None,

        'photo_name': first_photo.photo_name if first_photo else None,
        'photo_count': passport.photos.count(),
        'photos': photos_data,
        'usages': usage_items,
    }


@api_view(["POST"])
@permission_classes([AllowAny])
def create_passport_data_api(request):
    data = request.data
    files = request.FILES
    crop_group = _normalize_crop_group(data.get('crop_group'))

    accession_number = (data.get('accession_number') or '').strip()
    if not accession_number:
        return JsonResponse(
            {'success': False, 'message': 'Accession number is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if PassportData.objects.filter(accession_number=accession_number).exists():
        return JsonResponse(
            {'success': False, 'message': 'Accession number already exists.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if data.get('crop_group') and crop_group is None:
        return JsonResponse(
            {'success': False, 'message': 'Invalid crop group selected.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    crop = Crop.objects.create(
        crop_name=data.get('crop_name'),
        genus=data.get('genus'),
        species=data.get('species'),
        local_name=data.get('local_name'),
        crop_group=crop_group,
        species_authority=data.get('species_authority'),
        subtaxon=data.get('subtaxon'),
        accession_name=data.get('accession_name'),
        biologicalStatus=data.get('biologicalStatus'),
        storage=data.get('storage'),
        samplingMethod=data.get('samplingMethod'),
        materialCollected=data.get('materialCollected'),
        sampleType=data.get('sampleType'),
    )

    location = Location.objects.create(
        country=data.get('country'),
        province=data.get('province'),
        nearest_town=data.get('nearest_town'),
        barangay=data.get('barangay'),
        purok_or_sitio=data.get('purok_or_sitio'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        altitude=data.get('altitude'),
    )

    donor = Donor.objects.create(
        donor_name=data.get('donor_name'),
        growers_name=data.get('growers_name'),
        growers_contact_number=data.get('growers_contact_number'),
        donor_code=data.get('donor_code'),
        donor_accession_number=data.get('donor_accession_number'),
        location_duplicate_site=data.get('location_duplicate_site'),
        duplicate_institution_name=data.get('duplicate_institution_name'),
        other_donor_code_name=data.get('other_donor_code_name'),
    )

    topography = Topography.objects.create(
        site=data.get('site'),
        topography=data.get('topography'),
        soil_texture=data.get('soil_texture'),
        soil_color=data.get('soil_color'),
        drainage=data.get('drainage'),
        stoniness=data.get('stoniness'),
        diseases_and_pests=data.get('diseases_and_pests'),
        remarks=data.get('remarks'),
        cultural_practice=data.get('cultural_practice'),
        herbarium_specimen=_to_bool(data.get('herbarium_specimen')),
    )

    availability = Availability.objects.create(
        available_in_the_field=_to_bool(data.get('available_in_the_field')),
        available_at_in_vitro=_to_bool(data.get('available_at_in_vitro')),
        available_for_distribution=_to_bool(data.get('available_for_distribution')),
        status_of_harvest=data.get('status_of_harvest'),
        characterized=data.get('characterized'),
        field=data.get('field'),
    )

    photo = None
    uploaded_photos = files.getlist('photos')
    if not uploaded_photos and files.get('photo'):
        uploaded_photos = [files.get('photo')]
    photo_name = data.get('photo_name')

    user = request.user if getattr(request.user, 'is_authenticated', False) else None

    passport_data = PassportData.objects.create(
        accession_number=accession_number,
        old_accession_number=data.get('old_accession_number'),
        gb_number=data.get('gb_number'),
        collection_number=data.get('collection_number'),
        collection_country_code=data.get('collection_country_code'),
        collecting_date=data.get('collecting_date') or None,
        acquisition_date=data.get('acquisition_date') or None,
        collector=data.get('collector'),
        crop=crop,
        location=location,
        donor=donor,
        topography=topography,
        availability=availability,
        photo=None,
        created_by=user,
        updated_by=user,
    )

    created_photos = []
    for uploaded_photo in uploaded_photos:
        saved_photo = Photo.objects.create(
            passport_data=passport_data,
            photo=uploaded_photo,
            photo_name=photo_name or getattr(uploaded_photo, 'name', None),
        )
        created_photos.append(saved_photo)

    if not created_photos and photo_name:
        created_photos.append(
            Photo.objects.create(
                passport_data=passport_data,
                photo_name=photo_name,
            )
        )

    if created_photos:
        passport_data.photo = created_photos[0]
        passport_data.save(update_fields=['photo'])

    plant_parts = data.getlist('usage_plant_part')
    descriptions = data.getlist('usage_description')
    for part, desc in zip(plant_parts, descriptions):
        if (part or '').strip() or (desc or '').strip():
            Usage.objects.create(
                passport_data=passport_data,
                plant_part=(part or '').strip(),
                usage_description=(desc or '').strip(),
            )

    return JsonResponse(
        {
            'success': True,
            'message': 'Passport data created successfully.',
            'passport': {
                'id': passport_data.id,
                'gb_number': passport_data.gb_number,
                'accession_number': passport_data.accession_number,
                'collection_number': passport_data.collection_number,
                'crop_group': passport_data.crop.crop_group if passport_data.crop else None,
                'crop_name': passport_data.crop.crop_name if passport_data.crop else None,
                'genus': passport_data.crop.genus if passport_data.crop else None,
                'species': passport_data.crop.species if passport_data.crop else None,
                'photo_count': len(created_photos),
            },
        },
        status=status.HTTP_201_CREATED,
    )

# for view
@api_view(["GET"])
@permission_classes([AllowAny])
def list_passport_data_api(request):
    passports_qs = (
        PassportData.objects.select_related(
            'crop', 'location'
        )
        .all()
        .order_by('-created_at')
    )

    try:
        page = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        page = 1

    try:
        page_size = int(request.GET.get('page_size', 25))
    except (TypeError, ValueError):
        page_size = 25

    page = max(1, page)
    page_size = min(max(1, page_size), 100)

    paginator = Paginator(passports_qs, page_size)
    page_obj = paginator.get_page(page)

    passports = []
    for passport in page_obj.object_list:
        passports.append(
            {
                'id': passport.id,
                'gb_number': passport.gb_number,
                'accession_number': passport.accession_number,
                'collection_number': passport.collection_number,
                'crop_group': passport.crop.crop_group if passport.crop else None,
                'crop_name': passport.crop.crop_name if passport.crop else None,
                'genus': passport.crop.genus if passport.crop else None,
                'species': passport.crop.species if passport.crop else None,
                'country': passport.location.country if passport.location else None,
                'province': passport.location.province if passport.location else None,
            }
        )

    return JsonResponse(
        {
            'success': True,
            'passports': passports,
            'pagination': {
                'total': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'page_size': page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def list_compiled_characteristics_api(request):
    compiled_qs = (
        CompiledCharacteristic.objects.select_related(
            'passportData', 'passportData__crop', 'passportData__location'
        )
        .all()
        .order_by('-updatedAt', '-id')
    )

    try:
        page = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        page = 1

    try:
        page_size = int(request.GET.get('page_size', 25))
    except (TypeError, ValueError):
        page_size = 25

    page = max(1, page)
    page_size = min(max(1, page_size), 100)

    paginator = Paginator(compiled_qs, page_size)
    page_obj = paginator.get_page(page)

    records = []
    for compiled in page_obj.object_list:
        passport = compiled.passportData
        crop = passport.crop if passport else None
        location = passport.location if passport else None

        records.append(
            {
                'id': compiled.id,
                'source_model': compiled.source_model,
                'source_id': compiled.source_id,
                'passport_id': passport.id if passport else None,
                'accession_number': passport.accession_number if passport else None,
                'gb_number': passport.gb_number if passport else None,
                'old_accession_number': passport.old_accession_number if passport else None,
                'crop_name': crop.crop_name if crop else compiled.crop_name,
                'genus': crop.genus if crop else None,
                'species': crop.species if crop else None,
                'country': location.country if location else None,
                'province': location.province if location else None,
                'nearest_town': location.nearest_town if location else None,
                'barangay': location.barangay if location else None,
            }
        )

    return JsonResponse(
        {
            'success': True,
            'characterizations': records,
            'pagination': {
                'total': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'page_size': page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_passport_data_detail_api(request, passport_id):
    passport = (
        PassportData.objects.select_related(
            'crop', 'location', 'donor', 'topography', 'availability', 'photo'
        )
        .prefetch_related('usages', 'photos')
        .filter(id=passport_id)
        .first()
    )

    if passport is None:
        return JsonResponse(
            {'success': False, 'message': 'Passport data not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    return JsonResponse(
        {'success': True, 'passport': _serialize_passport_full(passport, request)},
        status=status.HTTP_200_OK,
    )

@api_view(["POST"])
@permission_classes([AllowAny])
def upload_passportdata(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        user = request.user if getattr(request.user, 'is_authenticated', False) else None
        try:
            df = pd.read_excel(file)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Failed to read file: {str(e)}'}, status=400)

        total_rows = len(df)
        successful = 0
        failed = []

        for i, row in df.iterrows():
            gb_no = row.get('GB_No') if pd.notna(row.get('GB_No')) else None
            acce_no = row.get('Acce_No') if pd.notna(row.get('Acce_No')) else None
            old_acce_no = row.get('Old_Acce_No') if pd.notna(row.get('Old_Acce_No')) else None

            if not gb_no and not acce_no and not old_acce_no:
                continue

            # Check for duplicates
            duplicate = False
            reason = ''
            if acce_no and PassportData.objects.filter(accession_number=acce_no).exists():
                duplicate = True
                reason = 'Duplicate Accession Number'
            elif gb_no and PassportData.objects.filter(gb_number=gb_no).exists():
                duplicate = True
                reason = 'Duplicate GB Number'
            elif old_acce_no and PassportData.objects.filter(old_accession_number=old_acce_no).exists():
                duplicate = True
                reason = 'Duplicate Old Accession Number'

            if duplicate:
                failed.append({
                    'row': i+1,
                    'gb_number': gb_no,
                    'accession_number': acce_no,
                    'old_accession_number': old_acce_no,
                    'reason': reason
                })
                continue

            try:
                def get_val(col):
                    v = row.get(col)
                    return v if pd.notna(v) else None

                # Create related objects (Location, Crop, Donor, Topography, Availability)
                location = Location.objects.create(
                    country=get_val('Country'),
                    province=get_val('Province'),
                    nearest_town=get_val('Nearest_Town'),
                    barangay=get_val('Barangay'),
                    purok_or_sitio=get_val('Purok_or_Sitio'),
                    latitude=get_val('Latitude'),
                    longitude=get_val('Longitude'),
                    altitude=get_val('Altitude'),
                )
                crop = Crop.objects.create(
                    crop_group=get_val('Crop_Group'),
                    crop_name=get_val('Crop_Name'),
                    genus=get_val('Genus'),
                    species=get_val('Species'),
                    species_authority=get_val('Spauthor'),
                    subtaxon=get_val('Subtaxa'),
                    subtaxon_authority=get_val('SubtaAuthor'),
                    local_name=get_val('Local_Name'),
                    accession_name=get_val('Acce_Name'),
                    other_crop_name=get_val('OtherCropName'),
                    biologicalStatus=get_val('Biological_Status'),
                    storage=get_val('Storage'),
                    samplingMethod=get_val('Sampling_Method'),
                    materialCollected=get_val('Material_Collected'),
                    sampleType=get_val('Sample_Type'),
                )
                donor = Donor.objects.create(
                    growers_name=get_val('Growers_name'),
                    growers_contact_number=get_val('Contact_No'),
                    donor_code=get_val('Donor_Code'),
                    donor_accession_number=get_val('Donor_Acce_No'),
                    donor_name=get_val('Donor_Name'),
                    location_duplicate_site=get_val('Location_Duplicate_Site'),
                    duplicate_institution_name=get_val('Dupl_Inst_Name'),
                    other_donor_code_name=get_val('OtherDonorCodeName'),
                )
                topography = Topography.objects.create(
                    cultural_practice=get_val('Cultural_practice'),
                    herbarium_specimen=True if str(get_val('Herbarium_specimen')).strip().lower() == 'true' else False,
                    topography=get_val('Topography'),
                    site=get_val('Site'),
                    soil_texture=get_val('Soil_Texture'),
                    soil_color=get_val('Soil_Color'),
                    drainage=get_val('Drainage'),
                    stoniness=get_val('Stoniness'),
                    diseases_and_pests=get_val('Diseases_and_Pests'),
                    remarks=get_val('Remarks'),
                )
                # Field1-Field8
                field_numbers = []
                for n in range(1, 9):
                    field_col = f'Field{n}'
                    if field_col in row:
                        field_val = row[field_col]
                        if field_val is True or (pd.notna(field_val) and str(field_val).strip().lower() == 'true'):
                            field_numbers.append(str(n))
                field_value = ','.join(field_numbers) if field_numbers else None
                status_of_harvest = get_val('Status_of_harvest') or 'FALSE'
                availability = Availability.objects.create(
                    available_at_in_vitro=True if str(get_val('Available_at_In_Vitro')).strip().lower() == 'true' else False,
                    available_in_the_field=True if str(get_val('Available_in_the_Field')).strip().lower() == 'true' else False,
                    available_for_distribution=True if str(get_val('Available_for_distribution')).strip().lower() == 'true' else False,
                    status_of_harvest=status_of_harvest,
                    characterized=get_val('Characterized'),
                    field=field_value,
                )
                # Main PassportData
                def parse_date(val):
                    try:
                        if pd.isna(val): return None
                        return pd.to_datetime(val).date()
                    except Exception:
                        return None
                passport_data = PassportData.objects.create(
                    collection_country_code=get_val('Coll_Country_Code'),
                    accession_number=acce_no,
                    old_accession_number=old_acce_no,
                    gb_number=gb_no,
                    collection_number=get_val('Coll_No'),
                    collecting_date=parse_date(get_val('Coll_Date')),
                    acquisition_date=parse_date(get_val('Acq_Date')),
                    collector=get_val('Collectors'),
                    location=location,
                    crop=crop,
                    donor=donor,
                    topography=topography,
                    availability=availability,
                    created_by=user,
                )
                # Usages
                usage_columns = {
                    'Usage_Whole_plant': 'Whole plant',
                    'Usage_Young_shoot': 'Young shoot',
                    'Usage_Sprouts': 'Sprouts',
                    'Usage_Leaf': 'Leaf',
                    'Usage_Stem': 'Stem',
                    'Usage_Root_tuber': 'Root/Tuber',
                    'Usage_fruit': 'Fruit',
                    'Usage_Seeds': 'Seeds',
                }
                for col, part in usage_columns.items():
                    if col in row and pd.notna(row[col]):
                        Usage.objects.create(passport_data=passport_data, plant_part=part, usage_description=row[col])
                successful += 1
            except Exception as e:
                failed.append({
                    'row': i+1,
                    'gb_number': gb_no,
                    'accession_number': acce_no,
                    'old_accession_number': old_acce_no,
                    'reason': str(e)
                })

        return JsonResponse({
            'success': True,
            'summary': {
                'total': total_rows,
                'successful': successful,
                'failed': len(failed),
                'failures': failed
            }
        })
    return JsonResponse({'success': False, 'message': 'No file uploaded'}, status=400)


    

