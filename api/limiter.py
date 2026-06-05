from slowapi import Limiter
from slowapi.util import get_remote_address


# Inisialisasi global rate limiter menggunakan IP client
limiter = Limiter(key_func=get_remote_address)
