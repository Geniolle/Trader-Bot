from decimal import Decimal


def exponential_moving_average(values: list[Decimal], period: int) -> Decimal | None:
    if period <= 0:
        raise ValueError("period must be greater than zero")

    if len(values) < period:
        return None

    multiplier = Decimal("2") / Decimal(period + 1)

    ema = sum(values[:period]) / Decimal(period)

    for value in values[period:]:
        ema = (value - ema) * multiplier + ema

    return ema