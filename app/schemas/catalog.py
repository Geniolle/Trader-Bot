# app/schemas/catalog.py

from pydantic import BaseModel


class CatalogProductSummaryResponse(BaseModel):
    code: str
    label: str
    description: str
    total_subproducts: int
    total_items: int


class CatalogProductsResponse(BaseModel):
    products: list[CatalogProductSummaryResponse]


class CatalogSubproductResponse(BaseModel):
    code: str
    label: str
    description: str


class CatalogProductResponse(BaseModel):
    code: str
    label: str
    description: str
    subproducts: list[CatalogSubproductResponse]


class CatalogInstrumentResponse(BaseModel):
    symbol: str
    display_name: str
    base_asset: str
    quote_asset: str


class CatalogItemsResponse(BaseModel):
    product: str
    subproduct: str | None = None
    total_items: int
    items: list[CatalogInstrumentResponse]