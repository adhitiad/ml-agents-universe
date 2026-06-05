"""Verification script untuk Phase 1 — Shared Library."""

import sys


sys.path.insert(0, ".")


def main() -> None:
    print("=== VERIFIKASI PHASE 1: SHARED LIBRARY ===")
    print()

    # 1. Models
    print("--- [1/6] shared.models ---")
    from shared.models import (
        AgentConfig,
        AgentDomain,
        AgentState,
        APIResponse,
        ColumnDefinition,
        ColumnType,
        DataSchema,
        ErrorResponse,
        PaginatedResponse,
    )

    config = AgentConfig(name="Test Agent", domain=AgentDomain.NLP)
    state = AgentState(agent_config=config, current_agent="nlp")
    resp = APIResponse(data={"hello": "world"})
    err = ErrorResponse(status_code=404, error_type="NotFound", detail="Not found")
    paged = PaginatedResponse(items=[1, 2, 3], total=100, page=1, per_page=20)
    schema = DataSchema(
        name="test_schema",
        columns=[
            ColumnDefinition(name="id", type=ColumnType.INTEGER, nullable=False),
            ColumnDefinition(name="name", type=ColumnType.STRING),
        ],
    )
    print(f"  [OK] AgentConfig: {config.name} ({config.domain})")
    print(f"  [OK] AgentState: trace_id={state.trace_id[:8]}...")
    print(f"  [OK] APIResponse: success={resp.success}")
    print(f"  [OK] ErrorResponse: {err.status_code} {err.error_type}")
    print(
        f"  [OK] PaginatedResponse: {paged.total_pages} pages, has_next={paged.has_next}"
    )
    print(f"  [OK] DataSchema: {schema.name}, columns={schema.column_names}")
    print()

    # 2. Utils
    print("--- [2/6] shared.utils ---")
    from shared.utils import (
        clean_text,
        cosine_similarity,
        euclidean_distance,
        load_yaml_config,
        merge_configs,
        moving_average,
        normalize_min_max,
        simple_tokenize,
        truncate_text,
    )

    cfg = load_yaml_config("configs/global.yaml")
    app_name = cfg["app"]["name"]
    print(f"  [OK] load_yaml_config: {app_name}")
    merged = merge_configs({"a": 1, "b": {"c": 2}}, {"b": {"d": 3}})
    print(f"  [OK] merge_configs: {merged}")
    cleaned = clean_text("<b>Hello</b>  World  <br/>")
    print(f"  [OK] clean_text: '{cleaned}'")
    tokens = simple_tokenize("Hello World ML Agents")
    print(f"  [OK] simple_tokenize: {tokens}")
    truncated = truncate_text("This is a very long text that should be truncated", 25)
    print(f"  [OK] truncate_text: '{truncated}'")
    norm = normalize_min_max([1, 2, 3, 4, 5])
    print(f"  [OK] normalize_min_max: {norm}")
    sim = cosine_similarity([1, 0, 1], [1, 1, 0])
    print(f"  [OK] cosine_similarity: {sim:.4f}")
    dist = euclidean_distance([0, 0], [3, 4])
    print(f"  [OK] euclidean_distance: {dist:.1f}")
    ma = moving_average([1, 2, 3, 4, 5, 6], 3)
    print(f"  [OK] moving_average: {ma}")
    print()

    # 3. Monitoring
    print("--- [3/6] shared.monitoring ---")
    from shared.monitoring import (
        AlertRule,
        MetricsCollector,
        PIIScrubber,
        Timer,
    )

    scrubber = PIIScrubber()
    scrubbed = scrubber.scrub("Email: test@example.com, Phone: 081234567890")
    print(f"  [OK] PIIScrubber: {scrubbed}")
    metrics = MetricsCollector(prefix="test")
    metrics.increment("requests")
    metrics.increment("requests")
    metrics.gauge("memory_mb", 256.0)
    with Timer(metrics, "test_op") as t:
        _ = sum(range(100000))
    print(f"  [OK] MetricsCollector: counter={metrics.get_counter('requests')}")
    print(f"  [OK] Timer: {t.elapsed_ms:.2f}ms")
    rule = AlertRule(name="high_latency", metric_name="latency_ms", threshold=500.0)
    triggered = rule.evaluate(600.0)
    print(f"  [OK] AlertRule: triggered={triggered}")
    print()

    # 4. Data
    print("--- [4/6] shared.data ---")
    from shared.data import (
        CSVLoader,
        DataLoader,
        DataValidator,
        JSONLoader,
        ParquetLoader,
        QualityScorer,
        get_loader_for_file,
    )

    assert isinstance(CSVLoader(), DataLoader), "CSVLoader should implement DataLoader"
    assert isinstance(JSONLoader(), DataLoader), (
        "JSONLoader should implement DataLoader"
    )
    assert isinstance(ParquetLoader(), DataLoader), (
        "ParquetLoader should implement DataLoader"
    )
    loader = get_loader_for_file("test.csv")
    print("  [OK] DataLoader Protocol: CSVLoader, JSONLoader, ParquetLoader all pass")
    print(f"  [OK] get_loader_for_file('.csv'): {type(loader).__name__}")
    loader2 = get_loader_for_file("data.parquet")
    print(f"  [OK] get_loader_for_file('.parquet'): {type(loader2).__name__}")

    # Validate with DataValidator
    import polars as pl

    test_df = pl.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"]})
    validator = DataValidator()
    result = validator.validate(test_df, schema)
    print(
        f"  [OK] DataValidator: is_valid={result.is_valid}, errors={len(result.errors)}"
    )

    scorer = QualityScorer()
    score = scorer.score(test_df, schema)
    print(f"  [OK] QualityScorer: score={score:.3f}")
    print()

    # 5. Env
    print("--- [5/6] shared.env ---")
    from shared.env import (
        AppSettings,
        EnvironmentConfig,
        LLMSettings,
        ObservationSpace,
        StepResult,
    )

    env_config = EnvironmentConfig(name="test_env", max_steps=100)
    step = StepResult(observation={"price": 100.0}, reward=1.5)
    obs_space = ObservationSpace(shape=[4], dtype="float32", low=-1.0, high=1.0)
    settings = AppSettings()
    llm_settings = LLMSettings()
    print(
        f"  [OK] EnvironmentConfig: {env_config.name}, max_steps={env_config.max_steps}"
    )
    print(f"  [OK] StepResult: reward={step.reward}, done={step.done}")
    print(f"  [OK] ObservationSpace: shape={obs_space.shape}")
    print(
        f"  [OK] AppSettings: env={settings.app_env}, is_dev={settings.is_development}"
    )
    print(f"  [OK] LLMSettings: model={llm_settings.model_name}")
    print()

    # 6. Serving
    print("--- [6/6] shared.serving ---")
    from shared.serving import (
        create_app,
    )

    app = create_app(title="Test API", version="0.0.1")
    print(f"  [OK] create_app: {app.title} v{app.version}")
    print(f"  [OK] Routes: {[getattr(r, 'path', str(r)) for r in app.routes]}")
    print()

    print("=" * 50)
    print("=== SEMUA VERIFIKASI PHASE 1 BERHASIL! ===")
    print("=" * 50)


if __name__ == "__main__":
    main()
