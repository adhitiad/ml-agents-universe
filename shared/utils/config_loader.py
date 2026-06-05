"""YAML configuration loader dengan environment variable substitution.

Module ini menyediakan tools untuk:
- Load YAML config files dengan resolusi ${ENV_VAR} placeholders
- Deep merge multiple config dictionaries
- Load domain-specific configs dari configs/{domain}/config.yaml

Typical usage:
    from shared.utils.config_loader import load_yaml_config, get_domain_config

    global_config = load_yaml_config("configs/global.yaml")
    nlp_config = get_domain_config("nlp")
"""

from __future__ import annotations

import logging
import os
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


logger = logging.getLogger(__name__)

# Pattern untuk mendeteksi ${ENV_VAR} atau ${ENV_VAR:default_value}
_ENV_VAR_PATTERN: re.Pattern[str] = re.compile(
    r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::([^}]*))?\}"
)


def _resolve_env_vars(value: str) -> str:
    """Resolve environment variable placeholders dalam string.

    Mendukung format:
    - ${VAR_NAME} — gunakan env var, kosong jika tidak ada
    - ${VAR_NAME:default} — gunakan env var, fallback ke default

    Args:
        value: String yang mungkin mengandung ${...} placeholders.

    Returns:
        String dengan placeholders sudah di-resolve.
    """

    def _replacer(match: re.Match[str]) -> str:
        var_name = match.group(1)
        default_value = match.group(2)
        env_value = os.environ.get(var_name)
        if env_value is not None:
            return env_value
        if default_value is not None:
            return default_value
        logger.debug("Env var '%s' tidak ditemukan, gunakan string kosong", var_name)
        return ""

    return _ENV_VAR_PATTERN.sub(_replacer, value)


def _resolve_recursive(data: Any) -> Any:
    """Resolve env vars secara rekursif dalam nested data structure.

    Args:
        data: Dict, list, string, atau value lain.

    Returns:
        Data dengan semua string ${...} placeholders di-resolve.
    """
    if isinstance(data, str):
        return _resolve_env_vars(data)
    if isinstance(data, dict):
        return {key: _resolve_recursive(val) for key, val in data.items()}
    if isinstance(data, list):
        return [_resolve_recursive(item) for item in data]
    return data


def load_yaml_config(
    path: str | Path,
    resolve_env: bool = True,
) -> dict[str, Any]:
    """Load YAML configuration file.

    Args:
        path: Path ke YAML file.
        resolve_env: Jika True, resolve ${ENV_VAR} placeholders.

    Returns:
        Dictionary berisi konfigurasi.

    Raises:
        FileNotFoundError: Jika file tidak ditemukan.
        yaml.YAMLError: Jika YAML parsing gagal.
    """
    config_path = Path(path)
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file tidak ditemukan: {config_path}")

    logger.debug("Loading YAML config: %s", config_path)
    with config_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        logger.warning("Config file kosong: %s", config_path)
        return {}

    if not isinstance(data, dict):
        raise TypeError(
            f"YAML config harus berupa mapping/dict, got {type(data).__name__}"
        )

    if resolve_env:
        data = _resolve_recursive(data)

    logger.info("Config loaded: %s (%d keys)", config_path.name, len(data))
    return data


def merge_configs(*configs: dict[str, Any]) -> dict[str, Any]:
    """Deep merge multiple config dictionaries.

    Config yang diberikan belakangan akan override yang sebelumnya.
    Nested dicts akan di-merge secara rekursif, bukan di-replace.

    Args:
        *configs: Dua atau lebih config dicts untuk di-merge.

    Returns:
        Merged config dictionary.

    Example:
        base = {"a": 1, "b": {"c": 2, "d": 3}}
        override = {"b": {"c": 99}, "e": 5}
        result = merge_configs(base, override)
        # {"a": 1, "b": {"c": 99, "d": 3}, "e": 5}
    """
    if not configs:
        return {}

    result = deepcopy(configs[0])
    for config in configs[1:]:
        _deep_merge(result, config)
    return result


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> None:
    """In-place deep merge override into base.

    Args:
        base: Base dictionary (akan dimodifikasi).
        override: Override dictionary.
    """
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = deepcopy(value)


def get_domain_config(
    domain: str,
    configs_dir: str | Path = "configs",
    global_config_name: str = "global.yaml",
) -> dict[str, Any]:
    """Load domain-specific config yang sudah di-merge dengan global config.

    Urutan merge: global.yaml → {domain}/config.yaml
    (domain-specific override global).

    Args:
        domain: Nama domain (e.g., "nlp", "finance").
        configs_dir: Path ke direktori configs.
        global_config_name: Nama file global config.

    Returns:
        Merged config dictionary.

    Raises:
        FileNotFoundError: Jika config file tidak ditemukan.
    """
    configs_path = Path(configs_dir)

    # Load global config
    global_path = configs_path / global_config_name
    global_config = load_yaml_config(global_path) if global_path.is_file() else {}

    # Load domain config
    domain_path = configs_path / domain / "config.yaml"
    domain_config = load_yaml_config(domain_path)

    merged = merge_configs(global_config, domain_config)
    logger.info("Domain config loaded: %s (merged with global)", domain)
    return merged
