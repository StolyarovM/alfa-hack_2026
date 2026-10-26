
import httpx
from app.core.config import settings

async def get_company_data(inn: str) -> dict:
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(f"{settings.mock_api_url}/api/v1/companies/{inn}")
        r.raise_for_status()
        return r.json()

async def run_check(check_name: str, inn: str) -> dict:
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.post(f"{settings.mock_api_url}/api/v1/checks/{check_name}", json={"inn": inn})
        r.raise_for_status()
        return r.json()
