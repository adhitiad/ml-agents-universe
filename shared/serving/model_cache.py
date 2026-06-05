"""In-Memory Model Loading & Caching."""

import logging


logger = logging.getLogger(__name__)


class ModelCache:
    """Singleton untuk preload models saat startup (menghindari delay saat first request)."""

    _instance = None
    _models: dict = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_all_models(self):
        """Dipanggil saat FastAPI startup event."""
        logger.info("Memulai Model Warmup (Preloading)...")
        # Mock loading delay
        self._models["nlp_base"] = "loaded_nlp_weights"
        self._models["finance_base"] = "loaded_finance_weights"
        self._models["economy_base"] = "loaded_economy_weights"
        self._models["education_base"] = "loaded_education_weights"
        self._models["entertainment_base"] = "loaded_entertainment_weights"
        self._models["math_base"] = "loaded_math_weights"
        self._models["science_base"] = "loaded_science_weights"
        logger.info("Semua model berhasil di-load ke dalam Cache.")

    def get_model(self, name: str):
        return self._models.get(name)


model_cache = ModelCache()
