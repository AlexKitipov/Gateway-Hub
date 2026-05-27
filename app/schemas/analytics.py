from pydantic import BaseModel


class LinkAnalyticsResponse(BaseModel):
    link_code: str
    total_clicks: int
    unique_ips: int
    top_countries: list[tuple[str, int]]
    top_referrers: list[tuple[str, int]]
    clicks_by_date: list[tuple[str, int]]
    clicks_by_hour: list[tuple[int, int]]
