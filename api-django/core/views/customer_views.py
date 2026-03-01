from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from core.models import Customer

@login_required
def inventory_customer_list(request):
    search_query = request.GET.get('search')
    customer_queryset = Customer.objects.all().order_by('id')  # Ascending order by ID
    if search_query:
        customer_queryset = customer_queryset.filter(
            Q(customerName__icontains=search_query) |
            Q(designation__icontains=search_query) |
            Q(office__icontains=search_query) |
            Q(contactInfo__icontains=search_query) |
            Q(emailAddress__icontains=search_query)
        )
    paginator = Paginator(customer_queryset, 25)
    page = request.GET.get('page')
    customer_list = paginator.get_page(page)
    context = {
        'customer_list': customer_list,
        'search_query': search_query,
        'is_paginated': customer_list.has_other_pages(),
        'page_obj': customer_list,
    }
    return render(request, 'components/inventory_customer.html', context)

@login_required
@csrf_protect
def customer_add(request):
    if request.method == 'POST':
        customerName = request.POST.get('customerName')
        designation = request.POST.get('designation')
        office = request.POST.get('office')
        contactInfo = request.POST.get('contactInfo')
        emailAddress = request.POST.get('emailAddress')
        
        # Validation: Check if all required fields are provided
        if not all([customerName, designation, office, contactInfo, emailAddress]):
            messages.error(request, 'All fields are required.')
            return redirect(reverse('inventory_customer_list'))
        
        # Additional validation: Check email format (basic)
        if '@' not in emailAddress or '.' not in emailAddress:
            messages.error(request, 'Please enter a valid email address.')
            return redirect(reverse('inventory_customer_list'))
        
        try:
            customer = Customer.objects.create(
                customerName=customerName.strip(),
                designation=designation.strip(),
                office=office.strip(),
                contactInfo=contactInfo.strip(),
                emailAddress=emailAddress.strip(),
                updatedBy=request.user
            )
            messages.success(request, 'Customer added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding customer: {str(e)}')
        
        return redirect(reverse('inventory_customer_list'))
    else:
        return redirect(reverse('inventory_customer_list'))

@login_required
def customer_edit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'GET':
        # Return customer data as JSON for AJAX
        data = {
            'success': True,
            'customer': {
                'id': customer.id,
                'customerName': customer.customerName,
                'designation': customer.designation,
                'office': customer.office,
                'contactInfo': customer.contactInfo,
                'emailAddress': customer.emailAddress,
            }
        }
        return JsonResponse(data)
    
    elif request.method == 'POST':
        # Update customer data via AJAX
        customerName = request.POST.get('customerName')
        designation = request.POST.get('designation')
        office = request.POST.get('office')
        contactInfo = request.POST.get('contactInfo')
        emailAddress = request.POST.get('emailAddress')
        
        # Validation: Check if all required fields are provided
        if not all([customerName, designation, office, contactInfo, emailAddress]):
            return JsonResponse({'success': False, 'error': 'All fields are required.'})
        
        # Additional validation: Check email format (basic)
        if '@' not in emailAddress or '.' not in emailAddress:
            return JsonResponse({'success': False, 'error': 'Please enter a valid email address.'})
        
        try:
            customer.customerName = customerName.strip()
            customer.designation = designation.strip()
            customer.office = office.strip()
            customer.contactInfo = contactInfo.strip()
            customer.emailAddress = emailAddress.strip()
            customer.updatedBy = request.user
            customer.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["DELETE"])
def customer_delete(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    try:
        customer.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def _serialize_customer(customer):
    return {
        'id': customer.id,
        'customerName': customer.customerName,
        'designation': customer.designation,
        'office': customer.office,
        'contactInfo': customer.contactInfo,
        'emailAddress': customer.emailAddress,
    }


def _is_valid_email(value):
    if not value:
        return True
    return '@' in value and '.' in value


@api_view(["GET"])
@permission_classes([AllowAny])
def list_customer_api(request):
    search_query = (request.GET.get('search') or '').strip()

    customers_qs = Customer.objects.all().order_by('-id')
    if search_query:
        customers_qs = customers_qs.filter(
            Q(customerName__icontains=search_query)
            | Q(designation__icontains=search_query)
            | Q(office__icontains=search_query)
            | Q(contactInfo__icontains=search_query)
            | Q(emailAddress__icontains=search_query)
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

    paginator = Paginator(customers_qs, page_size)
    page_obj = paginator.get_page(page)

    customers = [_serialize_customer(customer) for customer in page_obj.object_list]

    return JsonResponse(
        {
            'success': True,
            'customers': customers,
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
def get_customer_detail_api(request, customer_id):
    customer = Customer.objects.filter(id=customer_id).first()
    if customer is None:
        return JsonResponse(
            {'success': False, 'message': 'Customer not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    return JsonResponse(
        {'success': True, 'customer': _serialize_customer(customer)},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def create_customer_api(request):
    data = request.data

    customer_name = (data.get('customerName') or '').strip()
    designation = (data.get('designation') or '').strip()
    office = (data.get('office') or '').strip()
    contact_info = (data.get('contactInfo') or '').strip()
    email_address = (data.get('emailAddress') or '').strip()

    if not customer_name:
        return JsonResponse(
            {'success': False, 'message': 'Customer name is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if email_address and not _is_valid_email(email_address):
        return JsonResponse(
            {'success': False, 'message': 'Please enter a valid email address.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = request.user if getattr(request.user, 'is_authenticated', False) else None
    customer = Customer.objects.create(
        customerName=customer_name,
        designation=designation or None,
        office=office or None,
        contactInfo=contact_info or None,
        emailAddress=email_address or None,
        updatedBy=user,
    )

    return JsonResponse(
        {'success': True, 'message': 'Customer created successfully.', 'customer': _serialize_customer(customer)},
        status=status.HTTP_201_CREATED,
    )


@api_view(["PUT", "PATCH"])
@permission_classes([AllowAny])
def update_customer_api(request, customer_id):
    customer = Customer.objects.filter(id=customer_id).first()
    if customer is None:
        return JsonResponse(
            {'success': False, 'message': 'Customer not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    data = request.data

    customer_name = data.get('customerName', customer.customerName)
    designation = data.get('designation', customer.designation)
    office = data.get('office', customer.office)
    contact_info = data.get('contactInfo', customer.contactInfo)
    email_address = data.get('emailAddress', customer.emailAddress)

    customer_name = (customer_name or '').strip()
    designation = (designation or '').strip()
    office = (office or '').strip()
    contact_info = (contact_info or '').strip()
    email_address = (email_address or '').strip()

    if not customer_name:
        return JsonResponse(
            {'success': False, 'message': 'Customer name is required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if email_address and not _is_valid_email(email_address):
        return JsonResponse(
            {'success': False, 'message': 'Please enter a valid email address.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = request.user if getattr(request.user, 'is_authenticated', False) else None

    customer.customerName = customer_name
    customer.designation = designation or None
    customer.office = office or None
    customer.contactInfo = contact_info or None
    customer.emailAddress = email_address or None
    customer.updatedBy = user
    customer.save()

    return JsonResponse(
        {'success': True, 'message': 'Customer updated successfully.', 'customer': _serialize_customer(customer)},
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_customer_api(request, customer_id):
    customer = Customer.objects.filter(id=customer_id).first()
    if customer is None:
        return JsonResponse(
            {'success': False, 'message': 'Customer not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    customer.delete()
    return JsonResponse(
        {'success': True, 'message': 'Customer deleted successfully.'},
        status=status.HTTP_200_OK,
    )
