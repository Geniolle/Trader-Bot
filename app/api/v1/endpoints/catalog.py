# app/api/v1/endpoints/catalog.py

from fastapi import APIRouter, HTTPException

from app.schemas.catalog import (
    CatalogInstrumentResponse,
    CatalogItemsResponse,
    CatalogProductResponse,
    CatalogProductsResponse,
    CatalogProductSummaryResponse,
    CatalogSubproductResponse,
)

router = APIRouter(prefix="/catalog", tags=["catalog"])


CATALOG_DATA = {
    "forex": {
        "label": "Forex",
        "description": "Mercado cambial",
        "subproducts": {
            "major": {
                "label": "Major",
                "description": "Pares principais do Forex",
                "items": [
                    {
                        "symbol": "EURUSD",
                        "display_name": "EUR/USD",
                        "base_asset": "EUR",
                        "quote_asset": "USD",
                    },
                    {
                        "symbol": "GBPUSD",
                        "display_name": "GBP/USD",
                        "base_asset": "GBP",
                        "quote_asset": "USD",
                    },
                    {
                        "symbol": "USDJPY",
                        "display_name": "USD/JPY",
                        "base_asset": "USD",
                        "quote_asset": "JPY",
                    },
                    {
                        "symbol": "AUDUSD",
                        "display_name": "AUD/USD",
                        "base_asset": "AUD",
                        "quote_asset": "USD",
                    },
                    {
                        "symbol": "USDCAD",
                        "display_name": "USD/CAD",
                        "base_asset": "USD",
                        "quote_asset": "CAD",
                    },
                    {
                        "symbol": "USDCHF",
                        "display_name": "USD/CHF",
                        "base_asset": "USD",
                        "quote_asset": "CHF",
                    },
                    {
                        "symbol": "NZDUSD",
                        "display_name": "NZD/USD",
                        "base_asset": "NZD",
                        "quote_asset": "USD",
                    },
                ],
            }
        },
    },
    "crypto": {
        "label": "Crypto",
        "description": "Mercado de criptomoedas",
        "subproducts": {
            "spot": {
                "label": "Spot",
                "description": "Mercado spot de criptoativos",
                "items": [
                    {
                        "symbol": "BTCUSDT",
                        "display_name": "BTC/USDT",
                        "base_asset": "BTC",
                        "quote_asset": "USDT",
                    },
                    {
                        "symbol": "ETHUSDT",
                        "display_name": "ETH/USDT",
                        "base_asset": "ETH",
                        "quote_asset": "USDT",
                    },
                    {
                        "symbol": "SOLUSDT",
                        "display_name": "SOL/USDT",
                        "base_asset": "SOL",
                        "quote_asset": "USDT",
                    },
                ],
            }
        },
    },
}


def _build_products_response() -> CatalogProductsResponse:
    products: list[CatalogProductSummaryResponse] = []

    for product_code, product_data in CATALOG_DATA.items():
        subproducts = product_data["subproducts"]
        total_items = sum(len(subproduct["items"]) for subproduct in subproducts.values())

        products.append(
            CatalogProductSummaryResponse(
                code=product_code,
                label=product_data["label"],
                description=product_data["description"],
                total_subproducts=len(subproducts),
                total_items=total_items,
            )
        )

    products.sort(key=lambda item: item.label.lower())
    return CatalogProductsResponse(products=products)


@router.get("/products", response_model=CatalogProductsResponse)
def list_products() -> CatalogProductsResponse:
    return _build_products_response()


@router.get("/products/{product_code}", response_model=CatalogProductResponse)
def get_product(product_code: str) -> CatalogProductResponse:
    product = CATALOG_DATA.get(product_code)

    if product is None:
        raise HTTPException(status_code=404, detail=f"Product not found: {product_code}")

    subproducts = [
        CatalogSubproductResponse(
            code=subproduct_code,
            label=subproduct_data["label"],
            description=subproduct_data["description"],
        )
        for subproduct_code, subproduct_data in product["subproducts"].items()
    ]
    subproducts.sort(key=lambda item: item.label.lower())

    return CatalogProductResponse(
        code=product_code,
        label=product["label"],
        description=product["description"],
        subproducts=subproducts,
    )


@router.get(
    "/products/{product_code}/subproducts/{subproduct_code}",
    response_model=CatalogItemsResponse,
)
def get_subproduct_items(product_code: str, subproduct_code: str) -> CatalogItemsResponse:
    product = CATALOG_DATA.get(product_code)

    if product is None:
        raise HTTPException(status_code=404, detail=f"Product not found: {product_code}")

    subproduct = product["subproducts"].get(subproduct_code)

    if subproduct is None:
        raise HTTPException(
            status_code=404,
            detail=f"Subproduct not found: {product_code}/{subproduct_code}",
        )

    items = [
        CatalogInstrumentResponse(
            symbol=item["symbol"],
            display_name=item["display_name"],
            base_asset=item["base_asset"],
            quote_asset=item["quote_asset"],
        )
        for item in subproduct["items"]
    ]
    items.sort(key=lambda item: item.display_name.lower())

    return CatalogItemsResponse(
        product=product_code,
        subproduct=subproduct_code,
        total_items=len(items),
        items=items,
    )