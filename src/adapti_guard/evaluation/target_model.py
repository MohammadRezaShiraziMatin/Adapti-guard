"""Target LLM abstraction for real end-to-end security evaluation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import hashlib
import json
import logging
import os
import re
import threading
import time
from pathlib import Path
from typing import Any

import yaml

from src.adapti_guard.evaluation.llm_cache import LLMCache

logger = logging.getLogger(__name__)


@dataclass
class GenerationRequest:
    prompt: str
    system_prompt: str = ""
    model_id: str = ""
    temperature: float = 0.0
    max_tokens: int = 512
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationResult:
    text: str
    model_id: str
    latency_ms: float
    cache_hit: bool = False
    usage: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


class TargetModel(ABC):
    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult:
        raise NotImplementedError

    def generate_batch(
        self,
        requests: list[GenerationRequest],
    ) -> list[GenerationResult]:
        return [self.generate(req) for req in requests]


class MockTargetModel(TargetModel):
    """Unit tests only. Real experiments must not silently use this."""

    def __init__(self, response: str = "MOCK_RESPONSE"):
        self.response = response
        self.calls: list[GenerationRequest] = []

    def generate(self, request: GenerationRequest) -> GenerationResult:
        self.calls.append(request)
        return GenerationResult(
            text=self.response,
            model_id=request.model_id or "mock",
            latency_ms=0.0,
            cache_hit=False,
        )


class OpenRouterTargetModel(TargetModel):
    """OpenAI-compatible client for OpenRouter target inference."""

    def __init__(
        self,
        model_id: str,
        *,
        base_url: str = "https://openrouter.ai/api/v1",
        api_key: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 512,
        timeout_seconds: float = 120.0,
        max_retries: int = 3,
        retry_backoff_seconds: float = 2.0,
        cache: LLMCache | None = None,
    ):
        self.model_id = model_id
        self.base_url = base_url
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.cache = cache

        if not self.api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. "
                "Real experiments are BLOCKED without API credentials."
            )

        from openai import OpenAI

        self._client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout_seconds,
        )

    def generate(self, request: GenerationRequest) -> GenerationResult:
        model = request.model_id or self.model_id
        temperature = request.temperature if request.temperature is not None else self.temperature
        max_tokens = request.max_tokens or self.max_tokens

        cache_key = _cache_key(model, request.system_prompt, request.prompt, temperature, max_tokens)
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return GenerationResult(
                    text=cached["text"],
                    model_id=model,
                    latency_ms=0.0,
                    cache_hit=True,
                    usage=cached.get("usage", {}),
                    raw=cached.get("raw", {}),
                )

        messages: list[dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        last_error: str | None = None
        for attempt in range(self.max_retries + 1):
            start = time.perf_counter()
            try:
                response = self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                latency_ms = (time.perf_counter() - start) * 1000.0
                text = response.choices[0].message.content or ""
                usage = {}
                if response.usage:
                    usage = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }
                raw = {"id": response.id, "model": response.model}
                result = GenerationResult(
                    text=text,
                    model_id=model,
                    latency_ms=latency_ms,
                    cache_hit=False,
                    usage=usage,
                    raw=raw,
                )
                if self.cache:
                    self.cache.set(
                        cache_key,
                        {"text": text, "usage": usage, "raw": raw},
                    )
                return result
            except Exception as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt < self.max_retries:
                    time.sleep(self.retry_backoff_seconds * (2 ** attempt))
                else:
                    break

        return GenerationResult(
            text="",
            model_id=model,
            latency_ms=0.0,
            cache_hit=False,
            error=last_error or "unknown_error",
        )


class GroqTargetModel(TargetModel):
    """Groq OpenAI-compatible chat completions (`https://api.groq.com/openai/v1`).

    Isolated provider adapter. Does not alter OpenRouter/Ollama/Gemini clients.
    Optional ``reasoning_effort`` is passed only when configured (e.g. gpt-oss).
    """

    PROVIDER = "groq"
    DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(
        self,
        model_id: str = "openai/gpt-oss-120b",
        *,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 512,
        reasoning_effort: str | None = "low",
        timeout_seconds: float = 120.0,
        max_retries: int = 3,
        retry_backoff_seconds: float = 2.0,
        cache: LLMCache | None = None,
    ):
        from src.adapti_guard.experiments.env_loader import load_project_env

        load_project_env()
        self.model_id = model_id
        self.provider = self.PROVIDER
        self.base_url = base_url
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.reasoning_effort = reasoning_effort
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.cache = cache

        if not self.api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. "
                "Groq experiments are BLOCKED without API credentials."
            )

        from openai import OpenAI

        self._client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout_seconds,
        )

    def generate(self, request: GenerationRequest) -> GenerationResult:
        model = request.model_id or self.model_id
        temperature = (
            request.temperature if request.temperature is not None else self.temperature
        )
        max_tokens = request.max_tokens or self.max_tokens
        effort = None
        if request.metadata and "reasoning_effort" in request.metadata:
            effort = request.metadata.get("reasoning_effort")
        elif self.reasoning_effort:
            effort = self.reasoning_effort

        cache_key = _cache_key(
            f"groq:{model}:{effort or ''}",
            request.system_prompt,
            request.prompt,
            temperature,
            max_tokens,
        )
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return GenerationResult(
                    text=cached["text"],
                    model_id=model,
                    latency_ms=0.0,
                    cache_hit=True,
                    usage=cached.get("usage", {}),
                    raw=cached.get("raw", {}),
                )

        messages: list[dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        last_error: str | None = None
        last_status: int | None = None
        # Optional external retry accounting hook.
        # When set, it is called before each retry attempt (attempt > 0).
        retry_budget_hook = getattr(self, "_budget_retry_callback", None)
        for attempt in range(self.max_retries + 1):
            if attempt > 0 and retry_budget_hook is not None:
                retry_budget_hook()
            start = time.perf_counter()
            try:
                create_kwargs: dict[str, Any] = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                if effort:
                    # Groq gpt-oss supports reasoning_effort; pass via extra_body
                    # for OpenAI SDK compatibility.
                    create_kwargs["extra_body"] = {"reasoning_effort": effort}

                response = self._client.chat.completions.create(**create_kwargs)
                latency_ms = (time.perf_counter() - start) * 1000.0
                text = response.choices[0].message.content or ""
                usage: dict[str, Any] = {}
                if response.usage:
                    usage = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }
                finish = None
                if response.choices:
                    finish = getattr(response.choices[0], "finish_reason", None)
                raw = {
                    "id": getattr(response, "id", None),
                    "model": getattr(response, "model", model),
                    "provider": self.PROVIDER,
                    "finish_reason": finish,
                    "http_status": 200,
                    "reasoning_effort": effort,
                    "base_url": self.base_url,
                }
                result = GenerationResult(
                    text=text,
                    model_id=model,
                    latency_ms=latency_ms,
                    cache_hit=False,
                    usage=usage,
                    raw=raw,
                )
                if self.cache:
                    self.cache.set(
                        cache_key,
                        {"text": text, "usage": usage, "raw": raw},
                    )
                return result
            except Exception as exc:
                last_status = infer_http_status(exc)
                kind = _classify_http_status(last_status)
                last_error = (
                    f"{type(exc).__name__}: {exc} "
                    f"[http_status={last_status} class={kind}]"
                )
                if last_status in {401, 402, 403, 404}:
                    break
                retryable = last_status in {429, 500, 502, 503, 504} or last_status is None
                if retryable and attempt < self.max_retries:
                    time.sleep(self.retry_backoff_seconds * (2 ** attempt))
                    continue
                break

        return GenerationResult(
            text="",
            model_id=model,
            latency_ms=0.0,
            cache_hit=False,
            error=last_error or "unknown_error",
            raw={
                "provider": self.PROVIDER,
                "http_status": last_status,
                "error_class": _classify_http_status(last_status),
                "base_url": self.base_url,
            },
        )


class OllamaTargetModel(TargetModel):
    """Local Ollama inference via OpenAI-compatible API."""

    def __init__(
        self,
        model_id: str,
        *,
        base_url: str = "http://localhost:11434/v1",
        api_key: str = "ollama",
        temperature: float = 0.0,
        max_tokens: int = 512,
        timeout_seconds: float = 120.0,
        max_retries: int = 2,
        retry_backoff_seconds: float = 1.0,
        cache: LLMCache | None = None,
    ):
        self.model_id = model_id
        self.base_url = base_url
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.cache = cache

        from openai import OpenAI

        self._client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout_seconds,
        )

    @staticmethod
    def is_available(base_url: str = "http://localhost:11434") -> bool:
        import urllib.error
        import urllib.request

        try:
            req = urllib.request.Request(f"{base_url.rstrip('/')}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except (urllib.error.URLError, TimeoutError, OSError):
            return False

    def generate(self, request: GenerationRequest) -> GenerationResult:
        model = request.model_id or self.model_id
        temperature = request.temperature if request.temperature is not None else self.temperature
        max_tokens = request.max_tokens or self.max_tokens

        cache_key = _cache_key(model, request.system_prompt, request.prompt, temperature, max_tokens)
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return GenerationResult(
                    text=cached["text"],
                    model_id=model,
                    latency_ms=0.0,
                    cache_hit=True,
                    usage=cached.get("usage", {}),
                    raw=cached.get("raw", {}),
                )

        messages: list[dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        last_error: str | None = None
        for attempt in range(self.max_retries + 1):
            start = time.perf_counter()
            try:
                response = self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                latency_ms = (time.perf_counter() - start) * 1000.0
                text = response.choices[0].message.content or ""
                usage = {}
                if response.usage:
                    usage = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }
                raw = {"id": getattr(response, "id", ""), "model": response.model}
                result = GenerationResult(
                    text=text,
                    model_id=model,
                    latency_ms=latency_ms,
                    cache_hit=False,
                    usage=usage,
                    raw=raw,
                )
                if self.cache:
                    self.cache.set(cache_key, {"text": text, "usage": usage, "raw": raw})
                return result
            except Exception as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt < self.max_retries:
                    time.sleep(self.retry_backoff_seconds * (2 ** attempt))

        return GenerationResult(
            text="",
            model_id=model,
            latency_ms=0.0,
            cache_hit=False,
            error=last_error or "unknown_error",
        )


def _classify_http_status(status: int | None) -> str:
    if status == 401:
        return "authentication"
    if status == 402:
        return "insufficient_credit"
    if status == 403:
        return "access_permission"
    if status == 404:
        return "model_or_endpoint"
    if status == 408:
        return "timeout"
    if status == 429:
        return "rate_limit"
    if status is not None and status >= 500:
        return "provider_server_error"
    return "error"


_RETRY_IN_RE = re.compile(r"Please retry in ([0-9]+(?:\.[0-9]+)?)s", re.I)
_ERROR_CODE_RE = re.compile(r"Error code:\s*(\d+)", re.I)


def parse_retry_after_seconds(message: str, *, cap_seconds: float = 90.0) -> float | None:
    """Parse Gemini/OpenAI-style 'Please retry in Xs' without inventing delays."""
    if not message:
        return None
    match = _RETRY_IN_RE.search(message)
    if not match:
        return None
    delay = float(match.group(1))
    if delay < 0:
        return None
    return min(delay, cap_seconds)


def infer_http_status(exc: BaseException) -> int | None:
    """Extract HTTP status from SDK exceptions or 'Error code: NNN' text."""
    for attr in ("status_code", "code"):
        value = getattr(exc, attr, None)
        if isinstance(value, int) and value >= 100:
            return value
    resp = getattr(exc, "raw_response", None) or getattr(exc, "response", None)
    if resp is not None:
        code = getattr(resp, "status_code", None)
        if isinstance(code, int):
            return code
    match = _ERROR_CODE_RE.search(str(exc))
    if match:
        return int(match.group(1))
    return None


class GeminiTargetModel(TargetModel):
    """Google Gemini via the Interactions API (`google-genai`).

    Isolated provider adapter. Does not alter OpenRouter/Ollama clients.
    GenerationConfig supports seed and max_output_tokens; temperature and
    top_p are not accepted by this API path and are recorded as unsupported.
    """

    PROVIDER = "google"
    API = "interactions"
    UNSUPPORTED_GENERATION_PARAMS = ("temperature", "top_p")

    def __init__(
        self,
        model_id: str = "gemini-3.6-flash",
        *,
        api_key: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 512,
        seed: int = 42,
        timeout_seconds: float = 120.0,
        max_retries: int = 8,
        retry_backoff_seconds: float = 35.0,
        min_request_interval_seconds: float = 4.0,
        cache: LLMCache | None = None,
    ):
        from src.adapti_guard.experiments.env_loader import load_project_env

        load_project_env()
        self.model_id = model_id
        self.provider = self.PROVIDER
        self.api = self.API
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.seed = seed
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.min_request_interval_seconds = min_request_interval_seconds
        self.cache = cache
        self.unsupported_parameters = list(self.UNSUPPORTED_GENERATION_PARAMS)

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Gemini experiments are BLOCKED without API credentials."
            )

        from google import genai

        self._client = genai.Client(api_key=self.api_key)

    _shared_pace_lock = threading.Lock()
    _last_request_monotonic = 0.0
    _consecutive_429_failures = 0

    @classmethod
    def reset_quota_circuit(cls) -> None:
        """Clear the free-tier 429 circuit breaker (call at experiment start)."""
        cls._consecutive_429_failures = 0
        cls._last_request_monotonic = 0.0

    def _pace_requests(self) -> None:
        """Stay under free-tier RPM by serializing Gemini calls across target+judge."""
        interval = max(0.0, float(self.min_request_interval_seconds))
        with GeminiTargetModel._shared_pace_lock:
            now = time.monotonic()
            wait = interval - (now - GeminiTargetModel._last_request_monotonic)
            if wait > 0:
                time.sleep(wait)
            GeminiTargetModel._last_request_monotonic = time.monotonic()

    @staticmethod
    def _http_status(exc: BaseException) -> int | None:
        return infer_http_status(exc)

    def _retry_sleep_seconds(self, exc: BaseException, attempt: int) -> float:
        parsed = parse_retry_after_seconds(str(exc))
        if parsed is not None:
            return min(parsed + 1.0, 90.0)
        return min(self.retry_backoff_seconds * (2 ** attempt), 90.0)

    def generate(self, request: GenerationRequest) -> GenerationResult:
        model = request.model_id or self.model_id
        max_tokens = request.max_tokens or self.max_tokens
        seed = int((request.metadata or {}).get("seed", self.seed))

        cache_key = _cache_key(
            model, request.system_prompt, request.prompt, 0.0, max_tokens
        )
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return GenerationResult(
                    text=cached["text"],
                    model_id=model,
                    latency_ms=0.0,
                    cache_hit=True,
                    usage=cached.get("usage", {}),
                    raw=cached.get("raw", {}),
                )

        last_error: str | None = None
        last_status: int | None = None
        if getattr(GeminiTargetModel, "_consecutive_429_failures", 0) >= 3:
            return GenerationResult(
                text="",
                model_id=model,
                latency_ms=0.0,
                cache_hit=False,
                error=(
                    "quota_exhausted_circuit_open: "
                    "Gemini free-tier returned sustained HTTP 429"
                ),
                raw={
                    "provider": self.PROVIDER,
                    "api": self.API,
                    "http_status": 429,
                    "error_class": "rate_limit",
                },
            )
        for attempt in range(self.max_retries + 1):
            # Optional external retry accounting hook.
            # When set, it is called before each retry attempt (attempt > 0).
            retry_budget_hook = getattr(self, "_budget_retry_callback", None)
            if attempt > 0 and retry_budget_hook is not None:
                retry_budget_hook()
            self._pace_requests()
            start = time.perf_counter()
            try:
                kwargs: dict[str, Any] = {
                    "model": model,
                    "input": request.prompt,
                    "generation_config": {
                        "max_output_tokens": int(max_tokens),
                        "seed": seed,
                    },
                }
                if request.system_prompt:
                    kwargs["system_instruction"] = request.system_prompt

                response = self._client.interactions.create(**kwargs)
                latency_ms = (time.perf_counter() - start) * 1000.0
                text = getattr(response, "output_text", None) or ""
                usage_obj = getattr(response, "usage", None)
                usage: dict[str, Any] = {}
                if usage_obj is not None:
                    usage = {
                        "prompt_tokens": getattr(usage_obj, "total_input_tokens", None),
                        "completion_tokens": getattr(usage_obj, "total_output_tokens", None),
                        "total_tokens": getattr(usage_obj, "total_tokens", None),
                        "thought_tokens": getattr(usage_obj, "total_thought_tokens", None),
                    }
                errors = getattr(response, "errors", None)
                status = getattr(response, "status", None)
                if status == "failed" or errors:
                    err_msg = f"gemini_status={status} errors={errors}"
                    return GenerationResult(
                        text=text,
                        model_id=model,
                        latency_ms=latency_ms,
                        cache_hit=False,
                        usage=usage,
                        error=err_msg,
                        raw={
                            "id": getattr(response, "id", None),
                            "status": status,
                            "provider": self.PROVIDER,
                            "api": self.API,
                            "http_status": 200,
                            "unsupported_parameters": self.unsupported_parameters,
                        },
                    )
                raw = {
                    "id": getattr(response, "id", None),
                    "status": status,
                    "provider": self.PROVIDER,
                    "api": self.API,
                    "http_status": 200,
                    "seed": seed,
                    "max_output_tokens": int(max_tokens),
                    "unsupported_parameters": self.unsupported_parameters,
                }
                result = GenerationResult(
                    text=text,
                    model_id=model,
                    latency_ms=latency_ms,
                    cache_hit=False,
                    usage=usage,
                    raw=raw,
                )
                if self.cache:
                    self.cache.set(
                        cache_key,
                        {"text": text, "usage": usage, "raw": raw},
                    )
                GeminiTargetModel._consecutive_429_failures = 0
                return result
            except Exception as exc:
                last_status = self._http_status(exc)
                kind = _classify_http_status(last_status)
                last_error = (
                    f"{type(exc).__name__}: {exc} "
                    f"[http_status={last_status} class={kind}]"
                )
                retryable = last_status in {429, 500, 502, 503, 504} or last_status is None
                if last_status in {401, 402, 403, 404}:
                    break
                if retryable and attempt < self.max_retries:
                    delay = self._retry_sleep_seconds(exc, attempt)
                    logger.warning(
                        "Gemini retryable error http_status=%s; sleeping %.1fs (attempt %s/%s)",
                        last_status,
                        delay,
                        attempt + 1,
                        self.max_retries + 1,
                    )
                    time.sleep(delay)
                    continue
                break

        if last_status == 429:
            GeminiTargetModel._consecutive_429_failures = (
                getattr(GeminiTargetModel, "_consecutive_429_failures", 0) + 1
            )

        # Minimal fallback: Interactions API sometimes returns 502/connection failures.
        # Use generate_content for the same model so Gemini remains the independent judge.
        interactions_down = last_status in {500, 502, 503, 504} or last_status is None
        if interactions_down and last_status != 429:
            try:
                self._pace_requests()
                start = time.perf_counter()
                contents = request.prompt
                config: dict[str, Any] = {"max_output_tokens": int(max_tokens)}
                # seed may be unsupported on some generate_content paths; omit if rejected.
                try:
                    from google.genai import types as genai_types

                    gen_cfg = genai_types.GenerateContentConfig(
                        max_output_tokens=int(max_tokens),
                        system_instruction=request.system_prompt or None,
                    )
                    response = self._client.models.generate_content(
                        model=model,
                        contents=contents,
                        config=gen_cfg,
                    )
                except Exception:
                    response = self._client.models.generate_content(
                        model=model,
                        contents=(
                            f"{request.system_prompt}\n\n{contents}"
                            if request.system_prompt
                            else contents
                        ),
                    )
                latency_ms = (time.perf_counter() - start) * 1000.0
                text = getattr(response, "text", None) or ""
                usage_meta = getattr(response, "usage_metadata", None)
                usage: dict[str, Any] = {}
                if usage_meta is not None:
                    usage = {
                        "prompt_tokens": getattr(usage_meta, "prompt_token_count", None),
                        "completion_tokens": getattr(usage_meta, "candidates_token_count", None),
                        "total_tokens": getattr(usage_meta, "total_token_count", None),
                    }
                if text:
                    GeminiTargetModel._consecutive_429_failures = 0
                    result = GenerationResult(
                        text=text,
                        model_id=model,
                        latency_ms=latency_ms,
                        cache_hit=False,
                        usage=usage,
                        raw={
                            "provider": self.PROVIDER,
                            "api": "generate_content_fallback",
                            "http_status": 200,
                            "fallback_from": self.API,
                        },
                    )
                    if self.cache:
                        self.cache.set(
                            cache_key,
                            {"text": text, "usage": usage, "raw": result.raw},
                        )
                    return result
                last_error = f"generate_content_fallback_empty after interactions error: {last_error}"
            except Exception as exc:
                last_status = self._http_status(exc)
                last_error = (
                    f"generate_content_fallback_failed: {type(exc).__name__}: {exc} "
                    f"[after interactions: {last_error}]"
                )
                if last_status == 429:
                    GeminiTargetModel._consecutive_429_failures = (
                        getattr(GeminiTargetModel, "_consecutive_429_failures", 0) + 1
                    )

        return GenerationResult(
            text="",
            model_id=model,
            latency_ms=0.0,
            cache_hit=False,
            error=last_error or "unknown_error",
            raw={
                "provider": self.PROVIDER,
                "api": self.API,
                "http_status": last_status,
                "error_class": _classify_http_status(last_status),
            },
        )


class CerebrasTargetModel(TargetModel):
    """Cerebras OpenAI-compatible chat completions (`https://api.cerebras.ai/v1`)."""

    PROVIDER = "cerebras"
    DEFAULT_BASE_URL = "https://api.cerebras.ai/v1"

    def __init__(
        self,
        model_id: str = "qwen-3.8-27b",
        *,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 512,
        timeout_seconds: float = 120.0,
        max_retries: int = 4,
        retry_backoff_seconds: float = 2.0,
        cache: LLMCache | None = None,
    ):
        from src.adapti_guard.experiments.env_loader import load_project_env

        load_project_env()
        self.model_id = model_id
        self.provider = self.PROVIDER
        self.base_url = base_url
        self.api_key = (api_key or os.getenv("CEREBRAS_API_KEY") or "").strip()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.cache = cache

        if not self.api_key:
            raise RuntimeError(
                "CEREBRAS_API_KEY is not set. "
                "Cerebras judge experiments are BLOCKED without API credentials."
            )

        from openai import OpenAI

        self._client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout_seconds,
        )

    def generate(self, request: GenerationRequest) -> GenerationResult:
        model = request.model_id or self.model_id
        temperature = (
            request.temperature if request.temperature is not None else self.temperature
        )
        max_tokens = request.max_tokens or self.max_tokens
        cache_key = _cache_key(
            f"cerebras:{model}",
            request.system_prompt,
            request.prompt,
            temperature,
            max_tokens,
        )
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return GenerationResult(
                    text=cached["text"],
                    model_id=model,
                    latency_ms=0.0,
                    cache_hit=True,
                    usage=cached.get("usage", {}),
                    raw=cached.get("raw", {}),
                )

        messages: list[dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        last_error: str | None = None
        last_status: int | None = None
        retry_budget_hook = getattr(self, "_budget_retry_callback", None)
        for attempt in range(self.max_retries + 1):
            if attempt > 0 and retry_budget_hook is not None:
                retry_budget_hook()
            start = time.perf_counter()
            try:
                response = self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                latency_ms = (time.perf_counter() - start) * 1000.0
                text = response.choices[0].message.content or ""
                usage: dict[str, Any] = {}
                if response.usage:
                    usage = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }
                finish = None
                if response.choices:
                    finish = getattr(response.choices[0], "finish_reason", None)
                raw = {
                    "id": getattr(response, "id", None),
                    "model": getattr(response, "model", model),
                    "provider": self.PROVIDER,
                    "finish_reason": finish,
                    "http_status": 200,
                    "base_url": self.base_url,
                    "attempt": attempt,
                }
                result = GenerationResult(
                    text=text,
                    model_id=model,
                    latency_ms=latency_ms,
                    cache_hit=False,
                    usage=usage,
                    raw=raw,
                )
                if self.cache:
                    self.cache.set(
                        cache_key,
                        {"text": text, "usage": usage, "raw": raw},
                    )
                return result
            except Exception as exc:
                last_status = infer_http_status(exc)
                kind = _classify_http_status(last_status)
                last_error = (
                    f"{type(exc).__name__}: {exc} "
                    f"[http_status={last_status} class={kind}]"
                )
                if last_status in {401, 402, 403, 404}:
                    break
                retryable = last_status in {408, 429, 500, 502, 503, 504} or last_status is None
                if retryable and attempt < self.max_retries:
                    parsed = parse_retry_after_seconds(str(exc))
                    delay = parsed if parsed is not None else (
                        self.retry_backoff_seconds * (2 ** attempt)
                    )
                    logger.warning(
                        "Cerebras retryable error http_status=%s; sleeping %.1fs (attempt %s/%s)",
                        last_status,
                        delay,
                        attempt + 1,
                        self.max_retries + 1,
                    )
                    pass  # disabled retry sleep
                    continue
                break

        return GenerationResult(
            text="",
            model_id=model,
            latency_ms=0.0,
            cache_hit=False,
            error=last_error or "unknown_error",
            raw={
                "provider": self.PROVIDER,
                "http_status": last_status,
                "error_class": _classify_http_status(last_status),
                "base_url": self.base_url,
            },
        )


class LocalTransformersTargetModel(TargetModel):
    """Placeholder for future local inference. Not implemented."""

    def generate(self, request: GenerationRequest) -> GenerationResult:
        raise NotImplementedError(
            "LocalTransformersTargetModel is not implemented. "
            "Use OpenRouterTargetModel or mark experiment BLOCKED."
        )


def _cache_key(
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
) -> str:
    payload = json.dumps(
        {
            "model": model,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_model_config(path: str | Path = "configs/models.yaml") -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_target_model(
    config_key: str,
    *,
    config_path: str | Path = "configs/models.yaml",
    cache: LLMCache | None = None,
    cache_enabled: bool | None = None,
    allow_mock: bool = False,
) -> TargetModel:
    """Factory for configured target models. Never returns Mock unless allow_mock=True."""
    cfg = load_model_config(config_path)
    models = cfg.get("models", {})
    if config_key not in models:
        raise KeyError(f"Unknown model config key: {config_key}")

    spec = models[config_key]
    provider = spec.get("provider", "openrouter")
    cache_cfg = cfg.get("cache", {})

    def _resolve_cache() -> LLMCache | None:
        if cache is not None:
            return cache
        if cache_enabled is False:
            return None
        if cache_enabled is True or (
            cache_enabled is None and cache_cfg.get("enabled", True)
        ):
            return LLMCache(Path(cache_cfg.get("directory", ".llm_cache")))
        return None

    if provider == "mock":
        if not allow_mock:
            raise RuntimeError("MockTargetModel is not allowed for real experiments.")
        return MockTargetModel()

    if provider == "openrouter":
        openrouter = cfg.get("openrouter", {})
        llm_cache = _resolve_cache()

        return OpenRouterTargetModel(
            model_id=spec["model"],
            base_url=openrouter.get("base_url", "https://openrouter.ai/api/v1"),
            temperature=float(spec.get("temperature", 0.0)),
            max_tokens=int(spec.get("max_tokens", 512)),
            timeout_seconds=float(openrouter.get("timeout_seconds", 120)),
            max_retries=int(openrouter.get("max_retries", 3)),
            retry_backoff_seconds=float(openrouter.get("retry_backoff_seconds", 2.0)),
            cache=llm_cache,
        )

    if provider == "groq":
        groq_cfg = cfg.get("groq", {})
        llm_cache = _resolve_cache()
        effort = spec.get("reasoning_effort", groq_cfg.get("reasoning_effort", "low"))
        if effort in ("", "none", "null", None):
            effort = None
        return GroqTargetModel(
            model_id=spec["model"],
            base_url=groq_cfg.get(
                "base_url", "https://api.groq.com/openai/v1"
            ),
            temperature=float(spec.get("temperature", 0.0)),
            max_tokens=int(spec.get("max_tokens", 512)),
            reasoning_effort=str(effort) if effort else None,
            timeout_seconds=float(groq_cfg.get("timeout_seconds", 120)),
            max_retries=int(groq_cfg.get("max_retries", 3)),
            retry_backoff_seconds=float(groq_cfg.get("retry_backoff_seconds", 2.0)),
            cache=llm_cache,
        )

    if provider == "ollama":
        ollama_cfg = cfg.get("ollama", {})
        llm_cache = _resolve_cache()

        return OllamaTargetModel(
            model_id=spec["model"],
            base_url=ollama_cfg.get("base_url", "http://localhost:11434/v1"),
            temperature=float(spec.get("temperature", 0.0)),
            max_tokens=int(spec.get("max_tokens", 512)),
            timeout_seconds=float(ollama_cfg.get("timeout_seconds", 120)),
            max_retries=int(ollama_cfg.get("max_retries", 2)),
            retry_backoff_seconds=float(ollama_cfg.get("retry_backoff_seconds", 1.0)),
            cache=llm_cache,
        )

    if provider == "cerebras":
        cerebras_cfg = cfg.get("cerebras", {})
        llm_cache = _resolve_cache()
        return CerebrasTargetModel(
            model_id=spec["model"],
            base_url=cerebras_cfg.get("base_url", "https://api.cerebras.ai/v1"),
            temperature=float(spec.get("temperature", 0.0)),
            max_tokens=int(spec.get("max_tokens", 512)),
            timeout_seconds=float(cerebras_cfg.get("timeout_seconds", 120)),
            max_retries=int(cerebras_cfg.get("max_retries", 4)),
            retry_backoff_seconds=float(cerebras_cfg.get("retry_backoff_seconds", 2.0)),
            cache=llm_cache,
        )

    if provider in ("google", "gemini"):
        google_cfg = cfg.get("google", {})
        llm_cache = _resolve_cache()
        return GeminiTargetModel(
            model_id=spec["model"],
            temperature=float(spec.get("temperature", 0.0)),
            max_tokens=int(spec.get("max_tokens", 512)),
            seed=int(spec.get("seed", google_cfg.get("seed", 42))),
            timeout_seconds=float(google_cfg.get("timeout_seconds", 120)),
            max_retries=int(google_cfg.get("max_retries", 8)),
            retry_backoff_seconds=float(google_cfg.get("retry_backoff_seconds", 35.0)),
            min_request_interval_seconds=float(
                google_cfg.get("min_request_interval_seconds", 4.0)
            ),
            cache=llm_cache,
        )

    raise ValueError(f"Unsupported provider: {provider}")
