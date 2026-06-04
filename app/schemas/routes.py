from pydantic import BaseModel

class RoutePlaceItem(BaseModel):
    visit_order: int
    place_id: str
    name: str
    address: str
    lat: float
    lng: float
    image_url: str
    description: str
    tags: list[str] = []
    category: str

class RouteListItem(BaseModel):
    route_id: str
    title: str
    created_at: str
    place_count: int

class RouteCreateResponse(BaseModel):
    message: str
    route_id: str

class RouteDetailResponse(BaseModel):
    route_id: str
    title: str
    created_at: str
    description: str | None = None
    tags: list[str] = []
    places: list[RoutePlaceItem]

class RouteTransportationDetail(BaseModel):
    start: str
    arrival: str
    transferTimeText: str
    transferCount: int
    payment: int
    transport: str
    distance: str
    detailText: str

class RouteTransportationResponse(BaseModel):
    available: bool
    title: str
    totalTimeText: str
    summaryText: str
    firstStart: str
    lastArrival: str
    details: list[RouteTransportationDetail]
