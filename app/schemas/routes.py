from pydantic import BaseModel, Field

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

class RouteSaveFromRecommendationRequest(BaseModel):
    route_id: str = Field(
        ...,
        description="추천 카드/상세조회에서 전달하는 추천 동선 route_id",
    )

class RouteSaveFromRecommendationResponse(BaseModel):
    message: str
    route_id: str
    saved_route_id: str
    source_route_id: str
    source_detail_api_path: str
    saved_detail_api_path: str
    is_saved: bool = True

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
