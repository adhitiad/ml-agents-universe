"""Tools khusus untuk NLP Agent."""

import re
import urllib.request
from typing import Any

from pydantic import BaseModel, Field

from shared.agent.tools.base import BaseTool


# ==========================================
# Input Schemas
# ==========================================
class WebScraperInput(BaseModel):
    url: str = Field(..., description="URL website yang akan di-scrape.")

class TextCleanerInput(BaseModel):
    text: str = Field(..., description="Teks mentah yang akan dibersihkan.")
    remove_html: bool = Field(default=True, description="Hapus tag HTML jika ada.")

class TokenizerInput(BaseModel):
    text: str = Field(..., description="Teks yang akan di-tokenize.")

class SentimentInput(BaseModel):
    text: str = Field(..., description="Teks yang akan dianalisis sentimennya.")
    language: str = Field(default="id", description="Bahasa teks (id/en).")

class EntityInput(BaseModel):
    text: str = Field(..., description="Teks sumber ekstraksi.")


# ==========================================
# Tool Implementations
# ==========================================
class WebScraperTool(BaseTool):
    """Tool untuk mem-parsing dan mengambil teks dari URL secara sederhana (mock HTML tag removal)."""

    args_schema: type[BaseModel] | None = WebScraperInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="web_scraper", description="Scrape text from a URL.", **kwargs)

    def _run(self, url: str) -> str:
        # Peringatan: dalam environment sesungguhnya gunakan aiohttp & BeautifulSoup.
        # Ini adalah fallback fungsional tanpa dependensi eksternal untuk keperluan framework.
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read().decode('utf-8')
            # Sangat sederhana: strip HTML tags using Regex (hanya fallback demonstrasi)
            text = re.sub(r'<[^>]+>', ' ', html)
            return " ".join(text.split())[:1000] # kembalikan 1000 karakter pertama agar tak membanjiri konteks
        except Exception as e:
            return f"Error scraping {url}: {e!s}"


class TextCleanerTool(BaseTool):
    """Tool untuk membersihkan teks (menghapus spasi berlebih, karakter aneh, dll)."""

    args_schema: type[BaseModel] | None = TextCleanerInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="text_cleaner", description="Membersihkan teks kotor.", **kwargs)

    def _run(self, text: str, remove_html: bool = True) -> str:
        clean = text
        if remove_html:
            clean = re.sub(r'<[^>]+>', ' ', clean)
        # Hapus URL
        clean = re.sub(r'http[s]?://\S+', '', clean)
        # Hapus multiple whitespace
        clean = " ".join(clean.split())
        return clean


class TokenizerTool(BaseTool):
    """Tool untuk memecah teks menjadi token/kata."""

    args_schema: type[BaseModel] | None = TokenizerInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="tokenizer", description="Memecah teks menjadi daftar token kata.", **kwargs)

    def _run(self, text: str) -> dict[str, Any]:
        # Implementasi fallback regex dasar. Di prod, gunakan nltk/spacy.
        words = re.findall(r'\b\w+\b', text.lower())
        return {"token_count": len(words), "tokens": words}


class SentimentAnalyzerTool(BaseTool):
    """Tool mock untuk menganalisis sentimen."""

    args_schema: type[BaseModel] | None = SentimentInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="sentiment_analyzer", description="Analisis sentimen positif/negatif.", **kwargs)

    def _run(self, text: str, language: str = "id") -> dict[str, Any]:
        # Logika hardcode (mock analytic) tanpa dependensi LLM transformers
        pos_words = ["baik", "bagus", "keren", "hebat", "good", "great", "excellent"]
        neg_words = ["buruk", "jelek", "kecewa", "marah", "bad", "terrible", "awful"]

        lower_text = text.lower()
        pos_count = sum(1 for w in pos_words if w in lower_text)
        neg_count = sum(1 for w in neg_words if w in lower_text)

        if pos_count > neg_count:
            return {"sentiment": "positive", "score": 0.8}
        elif neg_count > pos_count:
            return {"sentiment": "negative", "score": -0.8}
        return {"sentiment": "neutral", "score": 0.0}


class EntityExtractorTool(BaseTool):
    """Tool mock untuk mengekstrak entitas bernama (NER)."""

    args_schema: type[BaseModel] | None = EntityInput

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="entity_extractor", description="Ekstrak entitas (Person, Org, Loc).", **kwargs)

    def _run(self, text: str) -> dict[str, list[str]]:
        # Ekstraksi berbasis huruf kapital sederhana sebagai tiruan NER
        words = text.split()
        potential_entities = [w for w in words if w.istitle() and len(w) > 2]
        return {"entities_found": potential_entities}
