"""Helper functions yang bersifat umum.

Module ini menyediakan:
- config_loader: YAML loading dengan env var substitution
- text_processing: Cleaning, tokenisasi, keyword extraction
- math_helpers: Normalization, distance metrics, statistics
- file_helpers: Safe read/write, atomic writes, directory helpers
"""

from shared.utils.config_loader import (
    get_domain_config,
    load_yaml_config,
    merge_configs,
)
from shared.utils.file_helpers import (
    atomic_write,
    ensure_directory,
    get_file_size,
    list_files,
    safe_read,
    safe_read_bytes,
    safe_write,
)
from shared.utils.math_helpers import (
    clamp,
    cosine_similarity,
    euclidean_distance,
    moving_average,
    normalize_min_max,
    normalize_z_score,
    percentage_change,
    safe_divide,
)
from shared.utils.text_processing import (
    clean_text,
    count_words,
    extract_keywords,
    normalize_whitespace,
    simple_tokenize,
    truncate_text,
)


__all__: list[str] = [
    # config_loader
    "load_yaml_config",
    "merge_configs",
    "get_domain_config",
    # file_helpers
    "safe_read",
    "safe_read_bytes",
    "safe_write",
    "atomic_write",
    "ensure_directory",
    "list_files",
    "get_file_size",
    # text_processing
    "clean_text",
    "simple_tokenize",
    "truncate_text",
    "extract_keywords",
    "count_words",
    "normalize_whitespace",
    # math_helpers
    "normalize_min_max",
    "normalize_z_score",
    "cosine_similarity",
    "euclidean_distance",
    "safe_divide",
    "moving_average",
    "clamp",
    "percentage_change",
]
