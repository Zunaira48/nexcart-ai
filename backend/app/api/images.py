from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/images", tags=["Images"])

ALLOWED_DOMAIN_SUFFIXES = ("flixcart.com",)

# Flixcart ke image servers hotlink-protection use karte hain — bina
# in headers ke real-browser-jaisi request nahi maante, aur reject
# kar dete hain.
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.flipkart.com/",
}


@router.get("/proxy")
async def proxy_image(url: str = Query(...)):
    parsed = urlparse(url)
    if not any(parsed.netloc.endswith(suffix) for suffix in ALLOWED_DOMAIN_SUFFIXES):
        raise HTTPException(status_code=400, detail="Ye domain allowed nahi hai")

    async with httpx.AsyncClient(timeout=8.0, headers=REQUEST_HEADERS) as client:
        try:
            resp = await client.get(url, follow_redirects=True)
        except httpx.HTTPError:
            raise HTTPException(status_code=502, detail="Image fetch nahi ho saki")

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Flixcart ne status {resp.status_code} diya")

    content_type = resp.headers.get("content-type", "image/jpeg")
    return StreamingResponse(iter([resp.content]), media_type=content_type)