from django.urls import path
from .views import hello
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_auth_views_path = Path(__file__).resolve().parent / "views" / "auth_views.py"
_auth_views_spec = spec_from_file_location("core_auth_views", _auth_views_path)
auth_views = module_from_spec(_auth_views_spec)
_auth_views_spec.loader.exec_module(auth_views)

_passport_views_path = Path(__file__).resolve().parent / "views" / "passportdata_views.py"
_passport_views_spec = spec_from_file_location("core_passportdata_views", _passport_views_path)
passport_views = module_from_spec(_passport_views_spec)
_passport_views_spec.loader.exec_module(passport_views)

_crop_characteristics_views_path = Path(__file__).resolve().parent / "views" / "cropcharacteristics_views.py"
_crop_characteristics_views_spec = spec_from_file_location("core_cropcharacteristics_views", _crop_characteristics_views_path)
crop_characteristics_views = module_from_spec(_crop_characteristics_views_spec)
_crop_characteristics_views_spec.loader.exec_module(crop_characteristics_views)

_customer_views_path = Path(__file__).resolve().parent / "views" / "customer_views.py"
_customer_views_spec = spec_from_file_location("core_customer_views", _customer_views_path)
customer_views = module_from_spec(_customer_views_spec)
_customer_views_spec.loader.exec_module(customer_views)

_product_views_path = Path(__file__).resolve().parent / "views" / "product_views.py"
_product_views_spec = spec_from_file_location("core_product_views", _product_views_path)
product_views = module_from_spec(_product_views_spec)
_product_views_spec.loader.exec_module(product_views)

_request_views_path = Path(__file__).resolve().parent / "views" / "request_views.py"
_request_views_spec = spec_from_file_location("core_request_views", _request_views_path)
request_views = module_from_spec(_request_views_spec)
_request_views_spec.loader.exec_module(request_views)

urlpatterns = [
    path("auth/signup/", auth_views.signup_view),
    path("auth/login/", auth_views.login_view),
    path("auth/logout/", auth_views.logout_view),
    path("auth/me/", auth_views.current_user_view),
    path("passport-data/list/", passport_views.list_passport_data_api),
    path("characterization-data/list/", passport_views.list_compiled_characteristics_api),
    path("characterization-data/upload/", crop_characteristics_views.upload_characteristics_data),
    path("characterization-data/<int:compiled_id>/", crop_characteristics_views.get_characteristic_detail_api),
    path("characterization-data/<int:compiled_id>/update/", crop_characteristics_views.update_characteristic_detail_api),
    path("passport-data/<int:passport_id>/", passport_views.get_passport_data_detail_api),
    path("passport-data/create/", passport_views.create_passport_data_api),
    path("passport-data/upload/", passport_views.upload_passportdata),
    path("customer/list/", customer_views.list_customer_api),
    path("customer/<int:customer_id>/", customer_views.get_customer_detail_api),
    path("customer/create/", customer_views.create_customer_api),
    path("customer/<int:customer_id>/update/", customer_views.update_customer_api),
    path("customer/<int:customer_id>/delete/", customer_views.delete_customer_api),
    path("product/list/", product_views.list_product_api),
    path("product/<int:product_id>/", product_views.get_product_detail_api),
    path("product/<int:product_id>/stock-movement/create/", product_views.create_product_stock_movement_api),
    path("product/create/", product_views.create_product_api),
    path("product/<int:product_id>/update/", product_views.update_product_api),
    path("product/<int:product_id>/delete/", product_views.delete_product_api),
    path("request/list/", request_views.list_request_api),
    path("request/create/", request_views.create_request_api),
    path("request/<int:request_id>/", request_views.get_request_detail_api),
    path("request/<int:request_id>/update/", request_views.update_request_api),
    path("request/validate-gb/", request_views.validate_request_gb_number_api),
    path("request/acquisitions/", request_views.get_request_available_acquisitions_api),
]