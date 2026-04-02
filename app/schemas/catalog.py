from pydantic import BaseModel


class CatalogInstrumentResponse(BaseModel):
    symbol: str
    display_name: str
    base_asset: str
    quote_asset: str


class CatalogSubproductResponse(BaseModel):
    code: str
    label: str
    description: str
    items: list[CatalogInstrumentResponse]


class CatalogProductResponse(BaseModel):
    code: str
    label: str
    description: str
    subproducts: list[CatalogSubproductResponse]


class CatalogProductSummaryResponse(BaseModel):
    code: str
    label: str
    description: str
    total_subproducts: int
    total_items: int


class CatalogProductListResponse(BaseModel):
    products: list[CatalogProductSummaryResponse]


class CatalogItemListResponse(BaseModel):
    product: str
    subproduct: str | None
    total_items: int
    items: list[CatalogInstrumentResponse]