from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
from django.utils.dateparse import parse_date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.models import Request, Customer, Product, PassportData, StockMovements


def _serialize_date(value):
    if value is None:
        return None
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return str(value)


def _serialize_request(request_obj):
    return {
        'id': request_obj.id,
        'customerId': request_obj.customer_id,
        'customerName': request_obj.customer.customerName if request_obj.customer else None,
        'purpose': request_obj.purpose,
        'cropName': request_obj.cropName,
        'useOfMaterials': request_obj.useOfMaterials,
        'projectTitle': request_obj.projectTitle,
        'materialNeeded': request_obj.materialNeeded,
        'supplyName': request_obj.supplyName,
        'productId': request_obj.product_id,
        'quantity': str(request_obj.quantity) if request_obj.quantity is not None else None,
        'unit': request_obj.unit,
        'requestDate': _serialize_date(request_obj.requestDate),
        'approved': request_obj.approved,
        'approvedDate': _serialize_date(request_obj.approvedDate),
        'approvedBy': request_obj.approvedBy,
        'released': request_obj.released,
        'releasedDate': _serialize_date(request_obj.releasedDate),
        'releasedBy': request_obj.releasedBy,
        'quarterReleased': request_obj.quarterReleased,
        'status': request_obj.status,
        'passportDataId': request_obj.passportData_id,
        'sourceAcquisitionId': request_obj.sourceAcquisition_id,
        'gbNumber': request_obj.passportData.gb_number if request_obj.passportData else None,
        'accessionNumber': request_obj.passportData.accession_number if request_obj.passportData else None,
        'oldAccessionNumber': request_obj.passportData.old_accession_number if request_obj.passportData else None,
    }


def _resolve_passport_for_request(data):
    accession_number = (data.get('accessionNumber') or data.get('accession_number') or '').strip()
    gb_number = (data.get('gbNumber') or data.get('gb_number') or '').strip()
    old_accession_number = (data.get('oldAccessionNumber') or data.get('old_accession_number') or '').strip()

    if accession_number:
        passport_data = PassportData.objects.select_related('crop').filter(accession_number=accession_number).first()
        if passport_data:
            return passport_data, accession_number

    if gb_number:
        passport_data = PassportData.objects.select_related('crop').filter(gb_number__iexact=gb_number).first()
        if passport_data:
            return passport_data, gb_number

    if old_accession_number:
        passport_data = PassportData.objects.select_related('crop').filter(old_accession_number=old_accession_number).first()
        if passport_data:
            return passport_data, old_accession_number

    return None, None


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_request_api(request):
    data = request.data

    customer_id = data.get('customerId') or data.get('customer')
    purpose = (data.get('purpose') or '').strip()
    project_title = (data.get('projectTitle') or '').strip()
    use_of_materials = (data.get('useOfMaterials') or '').strip()
    supply_name = (data.get('supplyName') or '').strip()
    quantity_raw = data.get('quantity')
    unit = (data.get('unit') or '').strip()
    source_acquisition_id = data.get('sourceAcquisitionId') or data.get('source_acquisition_id')

    has_passport_keys = any(
        [
            data.get('accessionNumber'),
            data.get('accession_number'),
            data.get('gbNumber'),
            data.get('gb_number'),
            data.get('oldAccessionNumber'),
            data.get('old_accession_number'),
        ]
    )

    if not all([customer_id, purpose, use_of_materials, supply_name, quantity_raw, source_acquisition_id]) or not has_passport_keys:
        return JsonResponse(
            {
                'success': False,
                'message': 'Customer, Passport reference (accession, GB, or old accession), Purpose, Use of Materials, Supply Name, Quantity, and Source Acquisition are required.',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    customer = Customer.objects.filter(id=customer_id).first()
    if customer is None:
        return JsonResponse(
            {'success': False, 'message': 'Invalid customer selected.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    passport_data, _ = _resolve_passport_for_request(data)
    if passport_data is None:
        return JsonResponse(
            {'success': False, 'message': 'Passport data not found. Lookup order: accession number, GB number, then old accession number.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    product = Product.objects.select_related('crop').filter(passportData=passport_data).first()
    if product is None:
        return JsonResponse(
            {'success': False, 'message': 'No product found for this GB number.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    source_acquisition = StockMovements.objects.filter(
        id=source_acquisition_id,
        movementType='ACQUISITION',
        product=product,
    ).first()
    if source_acquisition is None:
        return JsonResponse(
            {'success': False, 'message': 'Source acquisition not found.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        requested_quantity = Decimal(str(quantity_raw))
    except Exception:
        return JsonResponse(
            {'success': False, 'message': 'Invalid quantity format. Please enter a valid number.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if requested_quantity <= 0:
        return JsonResponse(
            {'success': False, 'message': 'Quantity must be greater than 0.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if requested_quantity > source_acquisition.quantity:
        return JsonResponse(
            {
                'success': False,
                'message': f'Cannot request {requested_quantity} units. Only {source_acquisition.quantity} units available in the selected acquisition.',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    crop_name = product.crop.crop_name if product.crop else 'N/A'
    material_needed = product.material or 'N/A'

    request_obj = Request.objects.create(
        customer=customer,
        purpose=purpose,
        cropName=crop_name,
        useOfMaterials=use_of_materials,
        projectTitle=project_title or None,
        materialNeeded=material_needed,
        supplyName=supply_name,
        product=product,
        passportData=passport_data,
        quantity=requested_quantity,
        unit=unit or source_acquisition.unit,
        requestDate=timezone.now().date(),
        status='Pending',
        sourceAcquisition=source_acquisition,
        createdBy=request.user,
        updatedBy=request.user,
    )

    return JsonResponse(
        {'success': True, 'message': 'Request added successfully.', 'request': _serialize_request(request_obj)},
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_request_api(request):
    search_query = (request.GET.get('search') or '').strip()
    status_filter = (request.GET.get('status') or '').strip().lower()

    requests_qs = Request.objects.select_related(
        'customer', 'product', 'passportData', 'seedLot', 'sourceAcquisition', 'createdBy', 'updatedBy'
    ).all().order_by('-createdAt', '-id')

    if not request.user.is_admin():
        requests_qs = requests_qs.filter(createdBy=request.user)

    if search_query:
        requests_qs = requests_qs.filter(
            Q(customer__customerName__icontains=search_query)
            | Q(purpose__icontains=search_query)
            | Q(cropName__icontains=search_query)
            | Q(projectTitle__icontains=search_query)
            | Q(materialNeeded__icontains=search_query)
            | Q(supplyName__icontains=search_query)
            | Q(status__icontains=search_query)
        )

    if status_filter == 'pending':
        requests_qs = requests_qs.filter(Q(status__iexact='pending') | Q(status__isnull=True, approved=False, released=False))
    elif status_filter == 'approved':
        requests_qs = requests_qs.filter(Q(status__iexact='approved') | Q(approved=True, released=False))
    elif status_filter == 'released':
        requests_qs = requests_qs.filter(Q(status__iexact='released') | Q(released=True))
    elif status_filter == 'cancelled':
        requests_qs = requests_qs.filter(status__iexact='cancelled')

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

    paginator = Paginator(requests_qs, page_size)
    page_obj = paginator.get_page(page)
    records = [_serialize_request(row) for row in page_obj.object_list]

    return JsonResponse(
        {
            'success': True,
            'requests': records,
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
@permission_classes([IsAuthenticated])
def validate_request_gb_number_api(request):
    accession_number = (request.GET.get('accession_number') or request.GET.get('accessionNumber') or '').strip()
    gb_number = (request.GET.get('gb_number') or request.GET.get('gbNumber') or '').strip()
    old_accession_number = (request.GET.get('old_accession_number') or request.GET.get('oldAccessionNumber') or '').strip()

    if not any([accession_number, gb_number, old_accession_number]):
        return JsonResponse(
            {'success': False, 'message': 'Accession number, GB number, or old accession number is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    lookup_data = {
        'accessionNumber': accession_number,
        'gbNumber': gb_number,
        'oldAccessionNumber': old_accession_number,
    }
    passport_data, _ = _resolve_passport_for_request(lookup_data)
    if passport_data is None:
        return JsonResponse(
            {'success': False, 'message': 'Passport data not found. Lookup order: accession number, GB number, then old accession number.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    product = Product.objects.select_related('crop').filter(passportData=passport_data).first()
    if product is None:
        return JsonResponse(
            {'success': False, 'message': 'No product found for this passport data.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    return JsonResponse(
        {
            'success': True,
            'data': {
                'product_id': product.id,
                'accession_number': passport_data.accession_number or 'N/A',
                'crop_name': product.crop.crop_name if product.crop else 'N/A',
                'material_needed': product.material or 'N/A',
                'description': product.description or 'N/A',
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_request_available_acquisitions_api(request):
    product_id = request.GET.get('product_id')
    if not product_id:
        return JsonResponse(
            {'success': False, 'message': 'Product ID is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    product = Product.objects.filter(id=product_id).first()
    if product is None:
        return JsonResponse(
            {'success': False, 'message': 'Product not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    acquisition_movements = StockMovements.objects.filter(
        product=product,
        movementType='ACQUISITION',
        quantity__gt=0,
    ).order_by('-movementDate', '-id')

    acquisitions_data = []
    for acq in acquisition_movements:
        acquisitions_data.append(
            {
                'id': acq.id,
                'movementDate': acq.movementDate.strftime('%Y-%m-%d') if acq.movementDate else None,
                'quantity': str(acq.quantity),
                'location': acq.location or '',
                'display_text': f"{acq.movementDate.strftime('%b %d, %Y')} - Available: {acq.quantity}",
            }
        )

    return JsonResponse(
        {'success': True, 'acquisitions': acquisitions_data},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_request_detail_api(request, request_id):
    request_obj = Request.objects.select_related(
        'customer', 'product', 'passportData', 'seedLot', 'sourceAcquisition', 'createdBy', 'updatedBy'
    ).filter(id=request_id).first()

    if request_obj is None:
        return JsonResponse(
            {'success': False, 'message': 'Request not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not request.user.is_admin() and request_obj.createdBy_id != request.user.id:
        return JsonResponse(
            {'success': False, 'message': 'Permission denied. You can only access your own requests.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    return JsonResponse(
        {'success': True, 'request': _serialize_request(request_obj)},
        status=status.HTTP_200_OK,
    )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_request_api(request, request_id):
    request_obj = Request.objects.select_related(
        'customer', 'product', 'passportData', 'sourceAcquisition'
    ).filter(id=request_id).first()

    if request_obj is None:
        return JsonResponse(
            {'success': False, 'message': 'Request not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not request.user.is_admin():
        return JsonResponse(
            {'success': False, 'message': 'Permission denied. Only admins can update request status.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    data = request.data
    new_status = (data.get('status') or '').strip().lower()
    approved_date_raw = (data.get('approvedDate') or '').strip()
    released_date_raw = (data.get('releasedDate') or '').strip()
    quarter_released = (data.get('quarterReleased') or '').strip()

    if new_status not in ['pending', 'approved', 'released', 'cancelled']:
        return JsonResponse(
            {'success': False, 'message': 'Invalid status. Use pending, approved, released, or cancelled.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    approved_date = parse_date(approved_date_raw) if approved_date_raw else None
    released_date = parse_date(released_date_raw) if released_date_raw else None

    if approved_date_raw and approved_date is None:
        return JsonResponse(
            {'success': False, 'message': 'Approved date must be in YYYY-MM-DD format.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if released_date_raw and released_date is None:
        return JsonResponse(
            {'success': False, 'message': 'Released date must be in YYYY-MM-DD format.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        if new_status == 'pending':
            request_obj.approved = False
            request_obj.released = False
            request_obj.approvedDate = None
            request_obj.approvedBy = None
            request_obj.releasedDate = None
            request_obj.releasedBy = None
            request_obj.quarterReleased = None

        elif new_status == 'approved':
            request_obj.approved = True
            request_obj.released = False
            request_obj.approvedDate = approved_date
            request_obj.approvedBy = request.user.get_full_name()
            request_obj.releasedDate = None
            request_obj.releasedBy = None
            request_obj.quarterReleased = None

        elif new_status == 'cancelled':
            request_obj.approved = False
            request_obj.released = False
            request_obj.approvedDate = None
            request_obj.approvedBy = None
            request_obj.releasedDate = None
            request_obj.releasedBy = None
            request_obj.quarterReleased = None

        elif new_status == 'released':
            if request_obj.sourceAcquisition is None:
                return JsonResponse(
                    {'success': False, 'message': 'Cannot release request: No source acquisition found.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if request_obj.quantity is None:
                return JsonResponse(
                    {'success': False, 'message': 'Cannot release request: Request quantity is missing.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if request_obj.sourceAcquisition.quantity < request_obj.quantity:
                return JsonResponse(
                    {
                        'success': False,
                        'message': f'Cannot release request: Only {request_obj.sourceAcquisition.quantity} units available, but {request_obj.quantity} units requested.',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if request_obj.released:
                return JsonResponse(
                    {'success': False, 'message': 'Request is already released.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                request_obj.approved = True
                request_obj.released = True
                request_obj.approvedDate = approved_date
                request_obj.approvedBy = request.user.get_full_name()
                request_obj.releasedDate = released_date or timezone.now().date()
                request_obj.releasedBy = request.user.get_full_name()
                request_obj.quarterReleased = quarter_released or None

                distribution_remarks = f"Released to customer: {request_obj.customer.customerName if request_obj.customer else 'Unknown'}"
                if request_obj.purpose:
                    distribution_remarks += f" - Purpose: {request_obj.purpose[:100]}..."
                if request_obj.projectTitle:
                    distribution_remarks += f" - Project: {request_obj.projectTitle[:50]}..."

                request_obj.sourceAcquisition.quantity -= request_obj.quantity
                request_obj.sourceAcquisition.updatedBy = request.user
                request_obj.sourceAcquisition.dateUpdated = timezone.now().date()
                request_obj.sourceAcquisition.save()

                StockMovements.objects.create(
                    product=request_obj.product,
                    movementType='DISTRIBUTION',
                    quantity=request_obj.quantity,
                    unit=request_obj.unit,
                    movementDate=request_obj.releasedDate,
                    remarks=distribution_remarks,
                    createdBy=request.user,
                    updatedBy=request.user,
                    dateUpdated=timezone.now().date(),
                )

        request_obj.status = new_status.title()
        request_obj.updatedBy = request.user
        request_obj.save()

        return JsonResponse(
            {'success': True, 'message': 'Request updated successfully.', 'request': _serialize_request(request_obj)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return JsonResponse(
            {'success': False, 'message': str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
