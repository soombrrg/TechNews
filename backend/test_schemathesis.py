import schemathesis


def get_jwt_token() -> str:
    """Get fresh JWT token (implement your logic)"""
    import requests

    response = requests.post(
        "http://localhost:8000/api/v1/auth/login/",
        json={"email": "a@m.ru", "password": "admin"},
    )
    return response.json()["access"]


# Apply auth to all tests
schema = schemathesis.openapi.from_url("http://localhost:8000/api/v1/docs/schema")
schema.config.output.sanitization.update(enabled=False)


# @schema.include(operation_id="create_booking_bookings_post").parametrize()
# @schema.include(method="POST", path_regex="/bookings/.*").parametrize()
@schema.parametrize()
def test_api(case: schemathesis.Case) -> None:
    case.call_and_validate(headers={"Authorization": f"Bearer {get_jwt_token()}"})
