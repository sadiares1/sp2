from django.apps import apps
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
import pandas as pd

from core.models import PassportData, CompiledCharacteristic


CHARACTERISTIC_SHEET_BY_CROP = {
	"Akapulko": "AkapulkoCharacteristics",
	"Banana": "BananaCharacteristics",
	"Bittergourd": "BittergourdCharacteristics",
	"Cashew": "CashewCharacteristics",
	"Cassava": "CassavaCharacteristics",
	"Citronella": "CitronellaCharacteristics",
	"Corn": "CornCharacteristics",
	"Cowpea": "CowpeaCharacteristics",
	"Eggplant": "EggplantCharacteristics",
	"Fruits": "FruitsCharacteristics",
	"Garden Spurge": "GardenspurgeCharacteristics",
	"Ginger": "GingerCharacteristics",
	"Gotu Kola": "GotukolaCharacteristics",
	"Guava": "GuavaCharacteristics",
	"Hyacinth": "HyacinthbeanCharacteristics",
	"Jatropha": "JatrophaCharacteristics",
	"Lagundi": "LagundiCharacteristics",
	"Lima": "LimabeanCharacteristics",
	"Luffa": "LuffaCharacteristics",
	"Malunggay": "MalunggayCharacteristics",
	"Mangosteen": "MangosteenCharacteristics",
	"Mung bea": "MungbeanCharacteristics",
	"Peanut": "PeanutCharacteristics",
	"Pepper": "PepperCharacteristics",
	"Pigeon pea": "PigeonpeaCharacteristics",
	"Pole Sitao": "PolesitaoCharacteristics",
	"Ricebean": "RicebeanCharacteristics",
	"Sabila": "SabilaCharacteristics",
	"Sambong": "SambongCharacteristics",
	"Snap bean": "SnapbeanCharacteristics",
	"Soybean": "SoybeanCharacteristics",
	"Squash": "SquashCharacteristics",
	"Sweet potato": "SweetpotatoCharacteristics",
	"Taro": "TaroCharacteristics",
	"Tomato": "TomatoCharacteristics",
	"Turmeric": "TurmericCharacteristics",
	"Winged bean": "WingedbeanCharacteristics",
	"Xanthosoma": "XanthosomaCharacteristics",
	"Yam": "YamCharacteristics",
	"Yerba buena": "YerbabuenaCharacteristics",
}


def _clean_cell(value):
	if pd.isna(value):
		return None
	if isinstance(value, str):
		cleaned = value.strip()
		return cleaned or None
	return value


def _find_passport_from_row(row):
	accession_value = _clean_cell(row.get("accession_number"))
	if accession_value:
		passport = PassportData.objects.filter(accession_number=str(accession_value)).select_related("crop").first()
		if passport:
			return passport, "accession_number", str(accession_value)

	gb_value = _clean_cell(row.get("gb_number"))
	if gb_value:
		passport = PassportData.objects.filter(gb_number=str(gb_value)).select_related("crop").first()
		if passport:
			return passport, "gb_number", str(gb_value)

	old_accession_value = _clean_cell(row.get("old_accession_number"))
	if old_accession_value:
		passport = PassportData.objects.filter(old_accession_number=str(old_accession_value)).select_related("crop").first()
		if passport:
			return passport, "old_accession_number", str(old_accession_value)

	return None, None, None


def _build_photo_url(request, file_field):
	if not file_field:
		return None

	try:
		return request.build_absolute_uri(file_field.url)
	except Exception:
		return None


@api_view(["POST"])
@permission_classes([AllowAny])
def upload_characteristics_data(request):
	upload_file = request.FILES.get("file")
	if upload_file is None:
		return JsonResponse({'success': False, 'message': 'No file uploaded.'}, status=400)

	filename = (upload_file.name or "").lower()
	if not filename.endswith('.xlsx'):
		return JsonResponse({'success': False, 'message': 'Only .xlsx files are allowed.'}, status=400)

	crop_name = (request.data.get("crop_name") or "").strip()
	if crop_name not in CHARACTERISTIC_SHEET_BY_CROP:
		return JsonResponse({'success': False, 'message': 'Invalid crop selected.'}, status=400)

	sheet_name = CHARACTERISTIC_SHEET_BY_CROP[crop_name]
	model = apps.get_model("core", sheet_name)
	if model is None:
		return JsonResponse({'success': False, 'message': f'Model not found for sheet {sheet_name}.'}, status=400)

	try:
		df = pd.read_excel(upload_file, sheet_name=sheet_name)
	except ValueError:
		return JsonResponse(
			{
				'success': False,
				'message': f'Sheet {sheet_name} was not found in the uploaded file.',
			},
			status=400,
		)
	except Exception as e:
		return JsonResponse({'success': False, 'message': f'Failed to read file: {str(e)}'}, status=400)

	df.columns = [str(col).strip() for col in df.columns]

	total_rows = len(df)
	successful = 0
	failed = []

	data_fields = [
		field
		for field in model._meta.fields
		if field.name not in {'id', 'passportData', 'createdAt', 'updatedAt'}
	]

	for i, row in df.iterrows():
		passport, matched_identifier_field, matched_identifier_value = _find_passport_from_row(row)
		if passport is None:
			failed.append(
				{
					'row': i + 2,
					'reason': 'Passport not found. Provide accession_number or gb_number or old_accession_number in the row.',
				}
			)
			continue

		if model.objects.filter(passportData=passport).exists():
			failed.append(
				{
					'row': i + 2,
					'identifier_field': matched_identifier_field,
					'identifier': matched_identifier_value,
					'reason': 'Duplicate characteristic for this passport.',
				}
			)
			continue

		payload = {'passportData': passport}
		for field in data_fields:
			field_name = field.name
			if field_name not in df.columns:
				continue

			raw_value = row.get(field_name)
			value = _clean_cell(raw_value)
			if value is None:
				continue

			if field.get_internal_type() == 'ImageField':
				continue

			try:
				if field.get_internal_type() == 'DateField':
					parsed_date = pd.to_datetime(value, errors='coerce')
					if pd.isna(parsed_date):
						continue
					payload[field_name] = parsed_date.date()
				else:
					payload[field_name] = field.to_python(value)
			except Exception:
				payload[field_name] = value

		try:
			model.objects.create(**payload)
			successful += 1
		except Exception as e:
			failed.append(
				{
					'row': i + 2,
					'identifier_field': matched_identifier_field,
					'identifier': matched_identifier_value,
					'reason': str(e),
				}
			)

	return JsonResponse(
		{
			'success': True,
			'summary': {
				'sheet': sheet_name,
				'total': total_rows,
				'successful': successful,
				'failed': len(failed),
				'failed_rows': failed,
			},
		},
		status=200,
	)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_characteristic_detail_api(request, compiled_id):
	compiled = (
		CompiledCharacteristic.objects.select_related("passportData", "passportData__crop")
		.filter(id=compiled_id)
		.first()
	)

	if compiled is None:
		return JsonResponse(
			{'success': False, 'message': 'Characteristic record not found.'},
			status=404,
		)

	model = apps.get_model("core", compiled.source_model)
	if model is None:
		return JsonResponse(
			{'success': False, 'message': 'Characteristic model not found.'},
			status=404,
		)

	instance = model.objects.filter(pk=compiled.source_id).first()
	if instance is None:
		return JsonResponse(
			{'success': False, 'message': 'Characteristic entry not found in source model.'},
			status=404,
		)

	passport = compiled.passportData
	crop_name = compiled.crop_name
	if passport and passport.crop:
		crop_name = passport.crop.crop_name

	fields = []
	photo = None
	for field in model._meta.fields:
		field_name = field.name
		if field_name in {"id", "passportData", "createdAt", "updatedAt"}:
			continue

		value = getattr(instance, field_name)
		if field.get_internal_type() == "ImageField":
			if value:
				photo = _build_photo_url(request, value)
			continue
		if hasattr(value, "name"):
			value = value.name
		if value == "":
			value = None

		fields.append(
			{
				"name": field_name,
				"label": field.verbose_name.title(),
				"value": str(value) if value is not None else None,
			}
		)

	return JsonResponse(
		{
			"success": True,
			"characteristic": {
				"id": compiled.id,
				"source_model": compiled.source_model,
				"source_id": compiled.source_id,
				"crop_name": crop_name,
				"photo": photo,
				"passport": {
					"id": passport.id if passport else None,
					"accession_number": passport.accession_number if passport else None,
					"gb_number": passport.gb_number if passport else None,
					"old_accession_number": passport.old_accession_number if passport else None,
				},
				"fields": fields,
			},
		},
		status=200,
	)


@api_view(["PATCH"])
@permission_classes([AllowAny])
def update_characteristic_detail_api(request, compiled_id):
	compiled = CompiledCharacteristic.objects.filter(id=compiled_id).first()
	if compiled is None:
		return JsonResponse({'success': False, 'message': 'Characteristic record not found.'}, status=404)

	model = apps.get_model("core", compiled.source_model)
	if model is None:
		return JsonResponse({'success': False, 'message': 'Characteristic model not found.'}, status=404)

	instance = model.objects.filter(pk=compiled.source_id).first()
	if instance is None:
		return JsonResponse({'success': False, 'message': 'Characteristic entry not found in source model.'}, status=404)

	data = request.data or {}
	updated_fields = []

	for field in model._meta.fields:
		field_name = field.name
		if field_name in {"id", "passportData", "createdAt", "updatedAt"}:
			continue
		if field.get_internal_type() == "ImageField":
			uploaded_file = request.FILES.get(field_name)
			if uploaded_file is not None:
				setattr(instance, field_name, uploaded_file)
				updated_fields.append(field_name)
			continue
		if field_name not in data:
			continue

		raw_value = data.get(field_name)
		if isinstance(raw_value, str):
			raw_value = raw_value.strip()

		if raw_value in [None, "", "-"]:
			parsed_value = None
		else:
			try:
				if field.get_internal_type() == 'DateField':
					parsed_date = pd.to_datetime(raw_value, errors='coerce')
					if pd.isna(parsed_date):
						return JsonResponse(
							{'success': False, 'message': f'Invalid date value for {field_name}.'},
							status=status.HTTP_400_BAD_REQUEST,
						)
					parsed_value = parsed_date.date()
				else:
					parsed_value = field.to_python(raw_value)
			except Exception:
				return JsonResponse(
					{'success': False, 'message': f'Invalid value for {field_name}.'},
					status=status.HTTP_400_BAD_REQUEST,
				)

		setattr(instance, field_name, parsed_value)
		updated_fields.append(field_name)

	if updated_fields:
		instance.save(update_fields=updated_fields + ["updatedAt"])

	return JsonResponse(
		{
			'success': True,
			'message': 'Characteristic updated successfully.',
			'updated_fields': updated_fields,
		},
		status=status.HTTP_200_OK,
	)
