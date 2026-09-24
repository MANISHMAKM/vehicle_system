# Vehicle Inventory & Booking REST API

Django REST Framework implementation of the Vehicle Inventory & Booking task.

## Project

- Project: `vehicle_system`
- App: `inventory`
- Backend: Django + Django REST Framework
- Database: SQLite by default, PostgreSQL supported through `DATABASE_URL`
- API documentation: Swagger/OpenAPI

## Features

### Vehicle

- Create vehicle
- List vehicles
- Retrieve vehicle details
- Update vehicle
- Delete vehicle
- Filter by brand
- Filter by fuel type
- Filter by availability

### Booking

- Create booking
- List bookings
- Retrieve booking details
- Validate customer phone number
- Validate start/end dates
- Prevent overlapping bookings
- Automatically calculate total amount
- Make vehicle unavailable after successful booking

## 1. Create virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. Install packages

```bash
pip install -r requirements.txt
```

## 3. Environment variables

Copy `.env.example` to `.env`.

Windows:

```bash
copy .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Change the secret key before production deployment.

## 4. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## 5. Create admin user

```bash
python manage.py createsuperuser
```

## 6. Run server

```bash
python manage.py runserver
```

Server:

```text
http://127.0.0.1:8000/
```

Swagger:

```text
http://127.0.0.1:8000/api/docs/
```

OpenAPI schema:

```text
http://127.0.0.1:8000/api/schema/
```

Admin:

```text
http://127.0.0.1:8000/admin/
```

# API Endpoints

## Vehicles

### List

```http
GET /api/vehicles/
```

### Create

```http
POST /api/vehicles/
```

Example:

```json
{
    "name": "Corolla",
    "brand": "Toyota",
    "year": 2024,
    "price_per_day": "2500.00",
    "fuel_type": "Petrol",
    "is_available": true
}
```

### Details

```http
GET /api/vehicles/1/
```

### Update

```http
PUT /api/vehicles/1/
```

Example:

```json
{
    "name": "Corolla",
    "brand": "Toyota",
    "year": 2025,
    "price_per_day": "2800.00",
    "fuel_type": "Hybrid",
    "is_available": true
}
```

### Delete

```http
DELETE /api/vehicles/1/
```

## Vehicle filtering

By brand:

```http
GET /api/vehicles/?brand=Toyota
```

By fuel type:

```http
GET /api/vehicles/?fuel_type=Electric
```

By availability:

```http
GET /api/vehicles/?is_available=true
```

Filters can also be combined:

```http
GET /api/vehicles/?brand=Toyota&fuel_type=Hybrid&is_available=true
```

# Booking API

## List bookings

```http
GET /api/bookings/
```

## Create booking

```http
POST /api/bookings/
```

Example:

```json
{
    "vehicle": 1,
    "customer_name": "Arjun",
    "customer_phone": "9876543210",
    "start_date": "2026-10-01",
    "end_date": "2026-10-05"
}
```

The response calculates:

```text
days = end_date - start_date
total_amount = days * price_per_day
```

For a vehicle costing ₹2500/day and a 4-day booking:

```text
4 * 2500 = ₹10000
```

`total_amount` does not need to be sent in the request.

## Booking details

```http
GET /api/bookings/1/
```

# Validation examples

## Start date in the past

Request:

```json
{
    "vehicle": 1,
    "customer_name": "Arjun",
    "customer_phone": "9876543210",
    "start_date": "2020-01-01",
    "end_date": "2020-01-05"
}
```

Response:

```json
{
    "start_date": [
        "Start date cannot be in the past."
    ]
}
```

## End date before/equal to start date

Response:

```json
{
    "end_date": [
        "End date must be after start date."
    ]
}
```

## Invalid phone

Response:

```json
{
    "customer_phone": [
        "Phone number must contain exactly 10 digits."
    ]
}
```

## Vehicle already booked

Response:

```json
{
    "vehicle": [
        "This vehicle is already booked for the selected date range."
    ]
}
```

## Vehicle unavailable

Response:

```json
{
    "vehicle": [
        "This vehicle is currently unavailable."
    ]
}
```

# Booking overlap logic

For an existing booking:

```text
start = 2026-10-01
end   = 2026-10-05
```

A new booking overlaps when:

```text
new_start < existing_end
AND
new_end > existing_start
```

This allows adjacent bookings such as:

```text
Existing: 2026-10-01 → 2026-10-05
New:      2026-10-05 → 2026-10-10
```

because the first booking ends when the second begins.

# Postman testing sequence

1. Start Django.
2. POST a vehicle.
3. Copy the returned vehicle `id`.
4. POST a booking using that vehicle ID.
5. Verify that `total_amount` is automatically calculated.
6. Verify that the vehicle becomes unavailable.
7. Try another booking for the same vehicle and verify the validation error.
8. Test invalid phone numbers.
9. Test past start dates.
10. Test invalid end dates.
11. Test GET vehicle filters.
12. Test PUT and DELETE vehicle endpoints.

# Example successful booking response

```json
{
    "id": 1,
    "vehicle": 1,
    "vehicle_name": "Corolla",
    "brand": "Toyota",
    "customer_name": "Arjun",
    "customer_phone": "9876543210",
    "start_date": "2026-10-01",
    "end_date": "2026-10-05",
    "rental_days": 4,
    "total_amount": "10000.00"
}
```

# Deployment

The project can be deployed on a cloud platform such as Render, Railway, or another Django-compatible host.

For production:

1. Set `DEBUG=False`.
2. Configure `ALLOWED_HOSTS`.
3. Use PostgreSQL.
4. Set a strong `SECRET_KEY`.
5. Configure `DATABASE_URL`.
6. Run:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

Example production start command:

```bash
gunicorn vehicle_system.wsgi:application
```

# Screen recording

For the requested 2–5 minute demonstration:

1. Show the project running.
2. Open Swagger at `/api/docs/`.
3. Create a vehicle.
4. Create a valid booking.
5. Show automatic `total_amount`.
6. Show vehicle availability changing to false.
7. Test an overlapping/unavailable booking.
8. Test invalid phone/date validation.
9. Show vehicle filtering.

**Demo Video:** https://docs.google.com/videos/d/1pcpRXPxCas32-niYy1OUt_6uc6Dy9BTjAKuEL5ehrzI/play?usp=sharing


# GitHub

Recommended repository structure:

```text
vehicle_system/
├── inventory/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── vehicle_system/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── .env.example
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```
