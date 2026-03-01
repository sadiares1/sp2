from django.contrib.auth import authenticate, login, logout
import re
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from core.models import Users


@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
	data = request.data

	email = (data.get("email") or "").strip().lower()
	password = data.get("password") or ""
	confirm_password = data.get("confirm_password") or ""
	first_name = (data.get("first_name") or "").strip()
	last_name = (data.get("last_name") or "").strip()
	middle_name = (data.get("middle_name") or "").strip()
	suffix = (data.get("suffix") or "").strip()

	if not email or not password or not first_name or not last_name:
		return Response(
			{"error": "email, password, first_name, and last_name are required."},
			status=status.HTTP_400_BAD_REQUEST,
		)

	if (
		len(password) < 8
		or re.search(r"[A-Z]", password) is None
		or re.search(r"[a-z]", password) is None
		or re.search(r"\d", password) is None
	):
		return Response(
			{"error": "Password must be at least 8 characters long and include at least 1 uppercase letter, 1 lowercase letter, and 1 number."},
			status=status.HTTP_400_BAD_REQUEST,
		)

	if password != confirm_password:
		return Response(
			{"error": "Passwords do not match."},
			status=status.HTTP_400_BAD_REQUEST,
		)

	if Users.objects.filter(email=email).exists():
		return Response(
			{"error": "Email is already registered."},
			status=status.HTTP_400_BAD_REQUEST,
		)

	base_username = email.split("@")[0]

	user = Users.objects.create_user(
		username=base_username,
		email=email,
		password=password,
		first_name=first_name,
		last_name=last_name,
		middle_name=middle_name or None,
		suffix=suffix or None,
	)

	return Response(
		{
			"message": "Signup successful.",
			"user": {
				"id": user.id,
				"email": user.email,
				"first_name": user.first_name,
				"last_name": user.last_name,
				"middle_name": user.middle_name,
				"suffix": user.suffix,
				"full_name": user.full_name,
				"role": user.role,
			},
		},
		status=status.HTTP_201_CREATED,
	)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
	data = request.data
	email = (data.get("email") or "").strip().lower()
	password = data.get("password") or ""

	if not email or not password:
		return Response(
			{"error": "email and password are required."},
			status=status.HTTP_400_BAD_REQUEST,
		)

	user = authenticate(request, email=email, password=password)
	if user is None:
		return Response(
			{"error": "Invalid credentials."},
			status=status.HTTP_401_UNAUTHORIZED,
		)

	if user.is_blocked:
		return Response(
			{"error": "Account is blocked."},
			status=status.HTTP_403_FORBIDDEN,
		)

	login(request, user)

	return Response(
		{
			"message": "Login successful.",
			"user": {
				"id": user.id,
				"email": user.email,
				"first_name": user.first_name,
				"last_name": user.last_name,
				"middle_name": user.middle_name,
				"suffix": user.suffix,
				"full_name": user.full_name,
				"role": user.role,
			},
		},
		status=status.HTTP_200_OK,
	)


@api_view(["POST"])
@permission_classes([AllowAny])
def logout_view(request):
	logout(request)
	return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
