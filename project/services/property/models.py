from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, field_validator, model_validator


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, allow_inf_nan=False)


AreaUnit = Literal["sq_ft", "sq_m", "perch", "acre", "hectare"]
Count = Annotated[StrictInt, Field(ge=0, le=32767)]
Area = Annotated[Decimal, Field(gt=0, max_digits=18, decimal_places=6)]


class Evidence(Input):
    approximate: StrictBool | None = None
    source_kind: Literal["seller"] = "seller"
    qualifier: str | None = None


class RoadWidth(Evidence):
    number_value: Annotated[Decimal, Field(gt=0, lt=10000000, decimal_places=3)]
    unit: Literal["ft", "m"]


class Draft(Input):
    property_type: Literal["house", "apartment", "land"]
    district: str | None = None
    town: str | None = None
    price_basis: Literal["total", "per_unit"] | None = None
    price_area_unit: AreaUnit | None = None
    entered_price: Annotated[Decimal, Field(gt=0, max_digits=18, decimal_places=2)] | None = None
    currency: Annotated[str, Field(pattern="^[A-Z]{3}$")] | None = None
    price_negotiable: StrictBool | None = None
    land_area: Area | None = None
    land_area_unit: AreaUnit | None = None
    land_area_approximate: StrictBool | None = None
    floor_area: Area | None = None
    floor_area_unit: Literal["sq_ft", "sq_m"] | None = None
    floor_area_approximate: StrictBool | None = None
    bedroom_count: Count | None = None
    bathroom_count: Count | None = None
    attached_bathroom_count: Count | None = None
    separate_toilet_count: Count | None = None
    house_storey_count: Count | None = None
    apartment_floor_no: Annotated[StrictInt, Field(ge=-32768, le=32767)] | None = None
    ground_floor_bedrooms: Count | None = None
    parking_spaces: Count | None = None
    covered_parking_spaces: Count | None = None
    vehicle_access: StrictBool | None = None
    construction_status: Literal["planned", "under_construction", "completed"] | None = None
    year_built: Count | None = None
    furnishing_status: Literal["unfurnished", "partly_furnished", "furnished"] | None = None
    has_mains_water: StrictBool | None = None
    has_well_water: StrictBool | None = None
    has_electricity: StrictBool | None = None
    has_garden: StrictBool | None = None
    has_boundary_wall: StrictBool | None = None
    standard_fact_evidence: dict[str, Evidence] = Field(default_factory=dict)
    access_road_width: RoadWidth | None = None
    access_road_width_approved_for_public: StrictBool | None = None

    @field_validator("standard_fact_evidence")
    @classmethod
    def dedicated_fields_only(cls, value):
        excluded = {
            "standard_fact_evidence",
            "access_road_width",
            "access_road_width_approved_for_public",
        }
        if value.keys() - (cls.model_fields.keys() - excluded):
            raise ValueError("Evidence requires a dedicated field")
        return value


class CreateDraft(Input):
    create_action_id: UUID
    draft: Draft


class SaveDraft(Input):
    edit_action_id: UUID
    parent_revision_id: UUID
    draft: Draft


class SaveShowcase(Input):
    action_id: UUID
    source_revision_id: UUID
    parent_showcase_id: UUID | None = None
    headline: Annotated[str, Field(min_length=1, max_length=240)]
    description: Annotated[str, Field(min_length=1, max_length=5000)]
    highlights: list[Annotated[str, Field(min_length=1, max_length=300)]] = Field(
        min_length=1, max_length=12
    )


class PublishListing(Input):
    action_id: UUID
    listing_revision_id: UUID
    showcase_id: UUID


class SearchQuery(Input):
    property_type: Literal["house", "apartment", "land"] | None = None
    district: Annotated[str, Field(min_length=1, max_length=160)] | None = None
    town: Annotated[str, Field(min_length=1, max_length=160)] | None = None
    currency: Annotated[str, Field(pattern="^[A-Z]{3}$")] | None = None
    min_price: Annotated[Decimal, Field(gt=0)] | None = None
    max_price: Annotated[Decimal, Field(gt=0)] | None = None
    min_bedrooms: Annotated[int, Field(ge=0)] | None = None
    min_bathrooms: Annotated[int, Field(ge=0)] | None = None
    min_land_area: Annotated[Decimal, Field(gt=0)] | None = None
    land_area_unit: AreaUnit | None = None
    min_floor_area: Annotated[Decimal, Field(gt=0)] | None = None
    floor_area_unit: Literal["sq_ft", "sq_m"] | None = None
    vehicle_access: Literal["any", "required", "confirmed", "none"] = "any"
    limit: Annotated[int, Field(ge=1, le=50)] = 20
    offset: Annotated[int, Field(ge=0, le=9223372036854775807)] = 0

    @model_validator(mode="after")
    def compatible_filters(self):
        if (self.min_price is not None or self.max_price is not None) and self.currency is None:
            raise ValueError("Price bounds require a currency")
        if self.min_price is not None and self.max_price is not None and self.min_price > self.max_price:
            raise ValueError("Minimum price must not exceed maximum price")
        for minimum, unit in ((self.min_land_area, self.land_area_unit),
                              (self.min_floor_area, self.floor_area_unit)):
            if (minimum is None) != (unit is None):
                raise ValueError("Minimum area and its unit must be supplied together")
        return self
