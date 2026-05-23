from pydantic import BaseModel

class RoutePlaceItem(BaseModel):
    visit_order: int
    place_id: str
    name: str
    address: str
    lat: float
    lng: float
    image_url: str

class RouteListItem(BaseModel):
    route_id: str
    title: str
    created_at: str
    place_count: int

class RouteDetailResponse(BaseModel):
    route_id: str
    title: str
    created_at: str
    places: list[RoutePlaceItem]
