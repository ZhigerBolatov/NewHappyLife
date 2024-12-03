from datetime import datetime


def datetime_serialize(datetime_str):
    datetime_obj = datetime.fromisoformat(datetime_str)
    result = {
        "date": datetime_obj.day,
        "month": datetime_obj.month,
        "year": datetime_obj.year,
        "time": datetime_obj.strftime("%H:%M")
    }
    return result


def get_full_data_for_assistant():
    from .models import Booking, User
    from .serializers import UserFullSerializer, BookingSerializer

    doctors = User.objects.filter(role='DC')
    data = UserFullSerializer(instance=doctors, many=True).data
    for doctor in data:
        bookings = Booking.objects.filter(doctor=doctor['id']).filter(status='Accepted')
        doctor['bookings'] = BookingSerializer(instance=bookings, many=True).data
    return data
