from fastapi import APIRouter

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/test")
def test_notification():
    pass

@router.post("/connect_telegram")
def connect_telegram():
    pass
