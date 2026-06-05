import importlib.util
import logging
import os
import sys

from shared.agent.base import BaseAgent


logger = logging.getLogger(__name__)


class PluginManager:
    """Manajer untuk memuat agen secara dinamis sebagai plugin."""

    def __init__(self):
        # Path absolut ke folder plugins
        self.plugins_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "plugins")
        )
        os.makedirs(self.plugins_dir, exist_ok=True)

        # Menyimpan cache agent class yang berhasil di-load
        self._loaded_agents: dict[str, type[BaseAgent]] = {}

    def discover_plugins(self) -> dict[str, dict]:
        """Mencari semua plugin yang tersedia di folder plugins."""
        available_plugins = {}
        if not os.path.exists(self.plugins_dir):
            return available_plugins

        for item in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, item)
            if os.path.isdir(plugin_path):
                # Asumsi: Setiap plugin harus punya file __init__.py atau manifest.json
                # Untuk penyederhanaan, kita anggap nama folder adalah nama plugin
                metadata_path = os.path.join(plugin_path, "metadata.json")
                if os.path.exists(metadata_path):
                    import json

                    try:
                        with open(metadata_path) as f:
                            metadata = json.load(f)
                        available_plugins[item] = metadata
                    except Exception as e:
                        logger.error(f"Gagal membaca metadata untuk plugin {item}: {e}")
                else:
                    # Default metadata jika tidak ada
                    available_plugins[item] = {
                        "name": item.capitalize(),
                        "description": "Third-party Agent Plugin",
                        "version": "1.0.0",
                    }
        return available_plugins

    def load_agent_class(self, plugin_name: str) -> type[BaseAgent] | None:
        """Memuat class agen dari folder plugin menggunakan importlib."""
        if plugin_name in self._loaded_agents:
            return self._loaded_agents[plugin_name]

        plugin_path = os.path.join(self.plugins_dir, plugin_name, "agent.py")
        if not os.path.exists(plugin_path):
            logger.error(f"Plugin {plugin_name} tidak memiliki file agent.py")
            return None

        module_name = f"plugins.{plugin_name}.agent"
        try:
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                # Cari class yang inherit dari BaseAgent
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BaseAgent)
                        and attr is not BaseAgent
                    ):
                        self._loaded_agents[plugin_name] = attr
                        logger.info(
                            f"Berhasil memuat agen: {attr_name} dari plugin {plugin_name}"
                        )
                        return attr

            logger.warning(f"Tidak ditemukan class turunan BaseAgent di {plugin_name}")
            return None
        except Exception as e:
            logger.error(f"Gagal memuat modul plugin {plugin_name}: {e}")
            return None
