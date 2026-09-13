from fastapi import APIRouter
from ..schemas import ApiResponse
from ..services.health_service import get_capabilities, overall_status

router = APIRouter()


@router.get("/", response_model=ApiResponse)
def health():
    caps = get_capabilities()
    status = overall_status(caps)
    data = {"status": status, "services": caps}
    return ApiResponse(success=True, data=data, error=None)
