# app/api/v1/endpoints/ws.py

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import suppress
from typing import Any

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger(__name__)


HEARTBEAT_INTERVAL_SECONDS = 15.0


def _safe_json_dumps(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, default=str)


async def _safe_send_json(websocket: WebSocket, payload: dict[str, Any]) -> bool:
    try:
      await websocket.send_text(_safe_json_dumps(payload))
      return True
    except WebSocketDisconnect:
      logger.info(
          "websocket_client_disconnected_during_send",
          extra={"event_payload": payload.get("event")},
      )
      return False
    except RuntimeError as exc:
      message = str(exc).lower()
      if "websocket is not connected" in message or "cannot call" in message:
          logger.info(
              "websocket_send_ignored_not_connected",
              extra={"event_payload": payload.get("event")},
          )
          return False
      logger.warning(
          "websocket_send_runtime_error",
          extra={
              "event_payload": payload.get("event"),
              "error": str(exc),
          },
      )
      return False
    except Exception as exc:
      logger.warning(
          "websocket_send_unexpected_error",
          extra={
              "event_payload": payload.get("event"),
              "error": str(exc),
          },
      )
      return False


async def _safe_receive_text(websocket: WebSocket) -> str | None:
    try:
        return await websocket.receive_text()
    except WebSocketDisconnect:
        return None
    except RuntimeError as exc:
        message = str(exc).lower()
        if "websocket is not connected" in message or "cannot call" in message:
            return None
        logger.warning("websocket_receive_runtime_error", extra={"error": str(exc)})
        return None
    except Exception as exc:
        logger.warning("websocket_receive_unexpected_error", extra={"error": str(exc)})
        return None


async def _heartbeat_loop(
    websocket: WebSocket,
    stop_event: asyncio.Event,
) -> None:
    heartbeat_count = 0

    while not stop_event.is_set():
        try:
            await asyncio.wait_for(
                stop_event.wait(),
                timeout=HEARTBEAT_INTERVAL_SECONDS,
            )
            break
        except asyncio.TimeoutError:
            pass

        heartbeat_count += 1

        sent = await _safe_send_json(
            websocket,
            {
                "event": "heartbeat",
                "data": {
                    "count": heartbeat_count,
                    "message": "alive",
                },
            },
        )

        if not sent:
            stop_event.set()
            break


@router.websocket("/ws")
async def websocket_feed(websocket: WebSocket) -> None:
    await websocket.accept()
    logger.info("websocket_connection_open")

    stop_event = asyncio.Event()
    heartbeat_task = asyncio.create_task(_heartbeat_loop(websocket, stop_event))

    selected_market_type: str | None = None
    selected_catalog: str | None = None
    selected_symbol: str | None = None
    selected_timeframe: str | None = None

    try:
        connected_ok = await _safe_send_json(
            websocket,
            {
                "event": "connected",
                "data": {
                    "message": "websocket connected",
                },
            },
        )
        if not connected_ok:
            return

        while not stop_event.is_set():
            raw_message = await _safe_receive_text(websocket)
            if raw_message is None:
                break

            if raw_message == "frontend_connected":
                ok = await _safe_send_json(
                    websocket,
                    {
                        "event": "echo",
                        "data": {
                            "message": "frontend_connected",
                        },
                    },
                )
                if not ok:
                    break
                continue

            try:
                payload = json.loads(raw_message)
            except json.JSONDecodeError:
                ok = await _safe_send_json(
                    websocket,
                    {
                        "event": "provider_error",
                        "data": {
                            "message": "Mensagem websocket inválida.",
                        },
                    },
                )
                if not ok:
                    break
                continue

            action = str(payload.get("action") or "").strip().lower()

            if action != "subscribe":
                ok = await _safe_send_json(
                    websocket,
                    {
                        "event": "provider_error",
                        "data": {
                            "message": f"Ação websocket não suportada: {action or '-'}",
                        },
                    },
                )
                if not ok:
                    break
                continue

            selected_market_type = (
                str(payload.get("market_type")).strip()
                if payload.get("market_type") is not None
                else None
            )
            selected_catalog = (
                str(payload.get("catalog")).strip()
                if payload.get("catalog") is not None
                else None
            )
            selected_symbol = (
                str(payload.get("symbol")).strip().upper()
                if payload.get("symbol") is not None
                else None
            )
            selected_timeframe = (
                str(payload.get("timeframe")).strip().lower()
                if payload.get("timeframe") is not None
                else None
            )

            subscribed_ok = await _safe_send_json(
                websocket,
                {
                    "event": "subscribed",
                    "data": {
                        "market_type": selected_market_type,
                        "catalog": selected_catalog,
                        "symbol": selected_symbol,
                        "timeframe": selected_timeframe,
                    },
                },
            )
            if not subscribed_ok:
                break

            # Mantém o socket vivo.
            # Se no teu projeto já existir um serviço que publica:
            # - initial_candles
            # - candle_tick
            # - candles_refresh
            # então integra-o aqui.
            #
            # O ponto principal desta reescrita é:
            # qualquer send_json deve passar por _safe_send_json(...)
            #
            # Exemplo:
            #
            # ok = await _safe_send_json(
            #     websocket,
            #     {
            #         "event": "initial_candles",
            #         "data": {
            #             "symbol": selected_symbol,
            #             "timeframe": selected_timeframe,
            #             "candles": candles_payload,
            #         },
            #     },
            # )
            # if not ok:
            #     break

    except WebSocketDisconnect:
        logger.info("websocket_connection_closed_by_client")
    except asyncio.CancelledError:
        logger.info("websocket_connection_cancelled")
        raise
    except Exception as exc:
        logger.exception("websocket_connection_unexpected_error: %s", exc)
    finally:
        stop_event.set()

        if heartbeat_task:
            heartbeat_task.cancel()
            with suppress(asyncio.CancelledError):
                await heartbeat_task

        with suppress(Exception):
            await websocket.close()

        logger.info("websocket_connection_closed")