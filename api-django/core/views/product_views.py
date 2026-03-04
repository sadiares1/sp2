from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from core.models import PassportData, Product, StockMovements
from decimal import Decimal


def _serialize_date(value):
    if value is None:
        return None
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    if isinstance(value, str):
        return value
    return str(value)


def _serialize_stock_movement(movement):
    return {
        'id': movement.id,
        'movementType': movement.movementType,
        'quantity': str(movement.quantity) if movement.quantity is not None else None,
        'unit': movement.unit,
        'movementDate': _serialize_date(movement.movementDate),
        'dateUpdated': _serialize_date(movement.dateUpdated),
        'location': movement.location,
        'shelfNo': movement.shelfNo,
        'trayNo': movement.trayNo,
        'bottleNo': movement.bottleNo,
        'packetNo': movement.packetNo,
        'activeBase': movement.activeBase,
        'batchReference': movement.batchReference,
        'pollType': movement.pollType,
        'remarks': movement.remarks,
        'dateOfRegeneration': _serialize_date(movement.dateOfRegeneration),
        'quarter': movement.quarter,
    }


def _serialize_product(product, include_movements=False):
    payload = {
        'id': product.id,
        'passportDataId': product.passportData_id,
        'accessionNumber': product.passportData.accession_number if product.passportData else None,
        'gbNumber': product.passportData.gb_number if product.passportData else None,
        'oldAccessionNumber': product.passportData.old_accession_number if product.passportData else None,
        'cropId': product.crop_id,
        'cropName': product.crop.crop_name if product.crop else None,
        'genus': product.crop.genus if product.crop else None,
        'species': product.crop.species if product.crop else None,
        'passportData': {
            'id': product.passportData_id,
            'gbNumber': product.passportData.gb_number if product.passportData else None,
            'accessionNumber': product.passportData.accession_number if product.passportData else None,
            'oldAccessionNumber': product.passportData.old_accession_number if product.passportData else None,
            'genus': product.crop.genus if product.crop else None,
            'species': product.crop.species if product.crop else None,
        } if product.passportData else None,
        'description': product.description,
        'material': product.material,
        'unitPrice': str(product.unitPrice) if product.unitPrice is not None else None,
        'remarks': product.remarks,
        'createdBy': {
            'id': product.createdBy_id,
            'fullName': product.createdBy.get_full_name() if product.createdBy else None,
            'username': product.createdBy.username if product.createdBy else None,
        } if product.createdBy else None,
        'createdDate': product.createdAt.isoformat() if product.createdAt else None,
        'updatedDate': product.updatedAt.isoformat() if product.updatedAt else None,
    }

    if include_movements:
        movements_qs = StockMovements.objects.filter(product=product).order_by('-movementDate', '-id')

        acquisitions = []
        disposals = []
        stock_takes = []
        distributions = []

        acquisition_total = Decimal('0')
        disposal_total = Decimal('0')
        stock_take_total = Decimal('0')
        distribution_total = Decimal('0')

        for movement in movements_qs:
            movement_data = _serialize_stock_movement(movement)
            quantity = movement.quantity if movement.quantity is not None else Decimal('0')

            if movement.movementType == 'ACQUISITION':
                acquisitions.append(movement_data)
                acquisition_total += quantity
            elif movement.movementType == 'DISPOSAL':
                disposals.append(movement_data)
                disposal_total += quantity
            elif movement.movementType == 'STOCK_TAKE':
                stock_takes.append(movement_data)
                stock_take_total += quantity
            elif movement.movementType == 'DISTRIBUTION':
                distributions.append(movement_data)
                distribution_total += quantity

        total_out = disposal_total + distribution_total
        net_acquisition = acquisition_total - total_out
        net_stock_takes = stock_take_total - total_out
        available_stock = net_acquisition + net_stock_takes

        payload['stockMovements'] = {
            'acquisition': acquisitions,
            'disposal': disposals,
            'stockTakes': stock_takes,
            'distribution': distributions,
        }
        payload['cumulativeAcquisition'] = str(net_acquisition)
        payload['cumulativeStockTakes'] = str(net_stock_takes)
        payload['availableStock'] = str(available_stock)

    return payload


def _parse_decimal_or_none(value):
    if value is None:
        return None
    text = str(value).strip()
    if text == '':
        return None
    try:
        return Decimal(text)
    except Exception:
        return None


def _resolve_passport_for_create(data):
    passport_data_id = data.get('passportDataId') or data.get('passportData')
    if passport_data_id:
        passport_data = PassportData.objects.select_related('crop').filter(id=passport_data_id).first()
        if passport_data:
            return passport_data

    accession_number = (data.get('accessionNumber') or data.get('accession_number') or '').strip()
    gb_number = (data.get('gbNumber') or data.get('gb_number') or '').strip()
    old_accession_number = (data.get('oldAccessionNumber') or data.get('old_accession_number') or '').strip()

    if accession_number:
        passport_data = PassportData.objects.select_related('crop').filter(accession_number=accession_number).first()
        if passport_data:
            return passport_data

    if gb_number:
        passport_data = PassportData.objects.select_related('crop').filter(gb_number=gb_number).first()
        if passport_data:
            return passport_data

    if old_accession_number:
        passport_data = PassportData.objects.select_related('crop').filter(old_accession_number=old_accession_number).first()
        if passport_data:
            return passport_data

    return None


@api_view(["GET"])
@permission_classes([AllowAny])
def list_product_api(request):
    search_query = (request.GET.get('search') or '').strip()

    products_qs = Product.objects.select_related('crop', 'passportData', 'createdBy').all().order_by('-id')
    if search_query:
        products_qs = products_qs.filter(
            Q(material__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(remarks__icontains=search_query)
            | Q(crop__crop_name__icontains=search_query)
            | Q(passportData__gb_number__icontains=search_query)
            | Q(passportData__accession_number__icontains=search_query)
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

    paginator = Paginator(products_qs, page_size)
    page_obj = paginator.get_page(page)

    products = [_serialize_product(product) for product in page_obj.object_list]

    return JsonResponse(
        {
            'success': True,
            'products': products,
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
def get_product_detail_api(request, product_id):
    product = Product.objects.select_related('crop', 'passportData', 'createdBy').filter(id=product_id).first()
    if product is None:
        return JsonResponse(
            {'success': False, 'message': 'Product not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    return JsonResponse(
        {'success': True, 'product': _serialize_product(product, include_movements=True)},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_product_api(request):
    data = request.data

    material = (data.get('material') or '').strip()
    description = (data.get('description') or '').strip()
    remarks = (data.get('remarks') or '').strip()
    unit_price_raw = data.get('unitPrice')

    if not material:
        return JsonResponse(
            {'success': False, 'message': 'Material is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    has_passport_keys = any(
        [
            data.get('passportDataId'),
            data.get('passportData'),
            data.get('accessionNumber'),
            data.get('accession_number'),
            data.get('gbNumber'),
            data.get('gb_number'),
            data.get('oldAccessionNumber'),
            data.get('old_accession_number'),
        ]
    )

    if not has_passport_keys:
        return JsonResponse(
            {
                'success': False,
                'message': 'Passport reference is required (passportDataId or accession_number or gb_number or old_accession_number).',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    passport_data = _resolve_passport_for_create(data)
    if passport_data is None:
        return JsonResponse(
            {
                'success': False,
                'message': 'Passport data not found. Lookup order: accession number, GB number, then old accession number.',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    unit_price = _parse_decimal_or_none(unit_price_raw)
    if unit_price_raw not in [None, ''] and unit_price is None:
        return JsonResponse(
            {'success': False, 'message': 'Invalid unit price format.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if unit_price is not None and unit_price < 0:
        return JsonResponse(
            {'success': False, 'message': 'Unit price cannot be negative.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = request.user
    product = Product.objects.create(
        passportData=passport_data,
        crop=passport_data.crop,
        description=description or None,
        material=material,
        unitPrice=unit_price,
        remarks=remarks or None,
        createdBy=user,
        updatedBy=user,
    )

    return JsonResponse(
        {'success': True, 'message': 'Product created successfully.', 'product': _serialize_product(product)},
        status=status.HTTP_201_CREATED,
    )


@api_view(["PUT", "PATCH"])
@permission_classes([AllowAny])
def update_product_api(request, product_id):
    product = Product.objects.select_related('crop', 'passportData', 'createdBy').filter(id=product_id).first()
    if product is None:
        return JsonResponse(
            {'success': False, 'message': 'Product not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    data = request.data

    material = data.get('material', product.material)
    description = data.get('description', product.description)
    remarks = data.get('remarks', product.remarks)
    unit_price_raw = data.get('unitPrice', product.unitPrice)
    passport_data_id = data.get('passportDataId') or data.get('passportData')

    material = (material or '').strip()
    description = (description or '').strip()
    remarks = (remarks or '').strip()

    if not material:
        return JsonResponse(
            {'success': False, 'message': 'Material is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    has_passport_update_keys = any(
        [
            passport_data_id,
            data.get('accessionNumber'),
            data.get('accession_number'),
            data.get('gbNumber'),
            data.get('gb_number'),
            data.get('oldAccessionNumber'),
            data.get('old_accession_number'),
        ]
    )

    if has_passport_update_keys:
        passport_data = _resolve_passport_for_create(data)
        if passport_data is None:
            return JsonResponse(
                {
                    'success': False,
                    'message': 'Passport data not found. Lookup order: accession number, GB number, then old accession number.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        product.passportData = passport_data
        product.crop = passport_data.crop

    unit_price = _parse_decimal_or_none(unit_price_raw)
    if unit_price_raw not in [None, ''] and unit_price is None:
        return JsonResponse(
            {'success': False, 'message': 'Invalid unit price format.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if unit_price is not None and unit_price < 0:
        return JsonResponse(
            {'success': False, 'message': 'Unit price cannot be negative.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = request.user if getattr(request.user, 'is_authenticated', False) else None

    product.material = material
    product.description = description or None
    product.unitPrice = unit_price
    product.remarks = remarks or None
    product.updatedBy = user
    product.save()

    return JsonResponse(
        {'success': True, 'message': 'Product updated successfully.', 'product': _serialize_product(product)},
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_product_api(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    if product is None:
        return JsonResponse(
            {'success': False, 'message': 'Product not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    product.delete()
    return JsonResponse(
        {'success': True, 'message': 'Product deleted successfully.'},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_product_stock_movement_api(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    if product is None:
        return JsonResponse(
            {'success': False, 'message': 'Product not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    data = request.data

    movement_type_raw = (data.get('movementType') or '').strip().upper()
    movement_type_map = {
        'ACQUISITION': 'ACQUISITION',
        'DISPOSAL': 'DISPOSAL',
        'STOCK_TAKE': 'STOCK_TAKE',
        'STOCK TAKE': 'STOCK_TAKE',
        'STOCKTAKE': 'STOCK_TAKE',
    }
    movement_type = movement_type_map.get(movement_type_raw)
    if movement_type is None:
        return JsonResponse(
            {'success': False, 'message': 'Invalid movement type. Use acquisition, disposal, or stock take.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    quantity = _parse_decimal_or_none(data.get('quantity'))
    if quantity is None:
        return JsonResponse(
            {'success': False, 'message': 'Quantity is required and must be a valid number.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if quantity < 0:
        return JsonResponse(
            {'success': False, 'message': 'Quantity cannot be negative.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    movement_date_raw = (data.get('movementDate') or '').strip()
    if not movement_date_raw:
        return JsonResponse(
            {'success': False, 'message': 'Movement date is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    movement_date = parse_date(movement_date_raw)
    if movement_date is None:
        return JsonResponse(
            {'success': False, 'message': 'Movement date must be a valid date in YYYY-MM-DD format.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = request.user

    movement = StockMovements.objects.create(
        product=product,
        movementType=movement_type,
        quantity=quantity,
        unit=(data.get('unit') or '').strip() or None,
        movementDate=movement_date,
        location=(data.get('location') or '').strip() or None,
        shelfNo=(data.get('shelfNo') or '').strip() or None,
        trayNo=(data.get('trayNo') or '').strip() or None,
        bottleNo=(data.get('bottleNo') or '').strip() or None,
        packetNo=(data.get('packetNo') or '').strip() or None,
        activeBase=(data.get('activeBase') or '').strip() or None,
        batchReference=(data.get('batchReference') or '').strip() or None,
        pollType=(data.get('pollType') or '').strip() or None,
        remarks=(data.get('remarks') or '').strip() or None,
        createdBy=user,
        updatedBy=user,
    )

    return JsonResponse(
        {
            'success': True,
            'message': 'Stock movement added successfully.',
            'stockMovement': _serialize_stock_movement(movement),
        },
        status=status.HTTP_201_CREATED,
    )
