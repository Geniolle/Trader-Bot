// TypeScript Interfaces for Response Schemas

export interface StrategyRunResponse {
    strategyId: string;
    runId: string;
    result: string;
    timestamp: Date;
}

export interface StrategyCaseResponse {
    caseId: string;
    strategyId: string;
    status: string;
    createdAt: Date;
}

export interface StrategyMetricsResponse {
    strategyId: string;
    metrics: {
        profit: number;
        loss: number;
        totalTrades: number;
    };
}

export interface CandleResponse {
    timestamp: Date;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
}

export interface HistoricalRunResponse {
    runId: string;
    strategyId: string;
    data: CandleResponse[];
}

export interface BatchHistoricalRunResponse {
    runs: HistoricalRunResponse[];
}

export interface RunDetailsResponse {
    runId: string;
    details: string;
    metrics: StrategyMetricsResponse;
}

export interface StrategyListItemResponse {
    strategyId: string;
    name: string;
    description: string;
    isActive: boolean;
}