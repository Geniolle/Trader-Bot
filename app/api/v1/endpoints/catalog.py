from fastapi import APIRouter, HTTPException

from app.core.instrument_catalog import InstrumentCatalogService
from app.schemas.catalog import (
    CatalogItemListResponse,
    CatalogProductListResponse,
    CatalogProductResponse,
    CatalogProductSummaryResponse,
)

router = APIRouter(prefix="/catalog", tags=["catalog"])


def _count_product_items(product: dict) -> int:
    total = 0
    for subproduct in product["subproducts"]:
        total += len(subproduct["items"])
    return total


@router.get("/products", response_model=CatalogProductListResponse)
def list_products() -> CatalogProductListResponse:
    service = InstrumentCatalogService()
    products = service.list_products()

    response_items = [
        CatalogProductSummaryResponse(
            code=product["code"],
            label=product["label"],
            description=product["description"],
            total_subproducts=len(product["subproducts"]),
            total_items=_count_product_items(product),
        )
        for product in products
    ]

    return CatalogProductListResponse(products=response_items)


@router.get("/products/{product_code}", response_model=CatalogProductResponse)
def get_product(product_code: str) -> CatalogProductResponse:
    service = InstrumentCatalogService()
    product = service.get_product(product_code)

    if product is None:
        raise HTTPException(status_code=404, detail=f"Product not found: {product_code}")

    return CatalogProductResponse(**product)


@router.get("/products/{product_code}/items", response_model=CatalogItemListResponse)
def list_product_items(product_code: str) -> CatalogItemListResponse:
    service = InstrumentCatalogService()
    product = service.get_product(product_code)

    if product is None:
        raise HTTPException(status_code=404, detail=f"Product not found: {product_code}")

    items = service.list_items(product_code=product_code)

    return CatalogItemListResponse(
        product=product_code.lower(),
        subproduct=None,
        total_items=len(items),
        items=items,
    )


@router.get(
    "/products/{product_code}/subproducts/{subproduct_code}",
    response_model=CatalogItemListResponse,
)
def list_subproduct_items(
    product_code: str,
    subproduct_code: str,
) -> CatalogItemListResponse:
    service = InstrumentCatalogService()
    product = service.get_product(product_code)

    if product is None:
        raise HTTPException(status_code=404, detail=f"Product not found: {product_code}")

    subproduct = service.get_subproduct(product_code, subproduct_code)
    if subproduct is None:
        raise HTTPException(
            status_code=404,
            detail=f"Subproduct not found: {product_code}/{subproduct_code}",
        )

    items = service.list_items(
        product_code=product_code,
        subproduct_code=subproduct_code,
    )

    return CatalogItemListResponse(
        product=product_code.lower(),
        subproduct=subproduct_code.lower(),
        total_items=len(items),
        items=items,
    )