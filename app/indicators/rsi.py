from decimal import Decimal


def relative_strength_index(values: list[Decimal], period: int) -> Decimal | None:
    if period <= 0:
        raise ValueError("period must be greater than zero")

    if len(values) < period + 1:
        return None

    gains: list[Decimal] = []
    losses: list[Decimal] = []

    for i in range(1, len(values)):
        change = values[i] - values[i - 1]
        gains.append(change if change > 0 else Decimal("0"))
        losses.append(-change if change < 0 else Decimal("0"))

    avg_gain = sum(gains[:period]) / Decimal(period)
    avg_loss = sum(losses[:period]) / Decimal(period)

    for i in range(period, len(gains)):
        avg_gain = ((avg_gain * Decimal(period - 1)) + gains[i]) / Decimal(period)
        avg_loss = ((avg_loss * Decimal(period - 1)) + losses[i]) / Decimal(period)

    if avg_loss == 0:
        return Decimal("100")

    rs = avg_gain / avg_loss
    rsi = Decimal("100") - (Decimal("100") / (Decimal("1") + rs))
    return rsi