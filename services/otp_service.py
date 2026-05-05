import random
import time

OTP_STORE = {}  # temporary memory store

OTP_EXPIRY_SECONDS = 300  # 5 min

def generate_otp(user_id):
    otp = str(random.randint(100000, 999999))

    OTP_STORE[user_id] = {
        "otp": otp,
        "time": time.time()
    }

    return otp


def verify_otp(user_id, otp_input):
    data = OTP_STORE.get(user_id)

    if not data:
        return False

    # expiry check
    if time.time() - data["time"] > OTP_EXPIRY_SECONDS:
        del OTP_STORE[user_id]
        return False

    # match check
    if data["otp"] == otp_input:
        del OTP_STORE[user_id]
        return True

    return False
