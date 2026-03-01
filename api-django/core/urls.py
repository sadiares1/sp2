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

urlpatterns = [
    path("hello/", hello),
    path("auth/signup/", auth_views.signup_view),
    path("auth/login/", auth_views.login_view),
    path("auth/logout/", auth_views.logout_view),
    path("passport-data/list/", passport_views.list_passport_data_api),
    path("passport-data/<int:passport_id>/", passport_views.get_passport_data_detail_api),
    path("passport-data/create/", passport_views.create_passport_data_api),
    path("passport-data/upload/", passport_views.upload_passportdata),
]