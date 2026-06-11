from app.data.population_decline_regions import POPULATION_DECLINE_REGIONS
from scripts import seed_population_decline_regions


def test_population_decline_region_list_has_expected_size_and_unique_codes() -> None:
    region_codes = [region.region_code for region in POPULATION_DECLINE_REGIONS]

    assert len(POPULATION_DECLINE_REGIONS) == 89
    assert len(region_codes) == len(set(region_codes))


def test_build_region_payloads_resolves_tour_api_sigungu_codes(monkeypatch) -> None:
    def fake_fetch_sigungu_codes(area_code: str) -> dict[str, str]:
        return {
            region.sigungu: str(index + 1)
            for index, region in enumerate(POPULATION_DECLINE_REGIONS)
            if region.area_code == area_code
        }

    monkeypatch.setattr(
        seed_population_decline_regions,
        "fetch_tour_api_sigungu_codes",
        fake_fetch_sigungu_codes,
    )

    payloads, unresolved = seed_population_decline_regions.build_region_payloads()

    assert unresolved == []
    assert len(payloads) == 89
    danyang = next(payload for payload in payloads if payload["region_code"] == "region-danyang")
    assert danyang["name"] == "단양군"
    assert danyang["sido"] == "충청북도"
    assert danyang["area_code"] == "33"
    assert danyang["sigungu_code"]
    assert danyang["is_population_decline"] is True
    assert danyang["is_active"] is True
