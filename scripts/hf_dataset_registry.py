"""Modul Registry dan Pengunduh Dataset HuggingFace untuk ML Agents Universe.

Modul ini mendefinisikan _DOMAIN_REGISTRY beserta fungsi unduh per-domain
menggunakan pustaka `datasets` dari HuggingFace.
"""

from typing import Any


try:
    from datasets import Dataset, DatasetDict, load_dataset
except ImportError:
    raise ImportError(
        "Harap install pustaka datasets terlebih dahulu: pip install datasets"
    )


def download_nlp_dataset() -> dict[str, Any]:
    """Download dataset NLP."""
    hf_id = "bitext/Bitext-customer-support-llm-chatbot-training-dataset"
    system_prompt = (
        "Kamu adalah NLP Agent. Tugasmu adalah memproses bahasa natural, "
        "menganalisis sentimen, mendeteksi intensi (intent), dan mendukung "
        "chatbot layanan pelanggan."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


def download_finance_dataset() -> dict[str, Any]:
    """Download dataset Finance."""
    hf_id = "zeroshot/twitter-financial-news-sentiment"
    system_prompt = (
        "Kamu adalah Finance Agent. Tugasmu adalah menganalisis berita keuangan, "
        "menilai sentimen pasar, dan memberikan wawasan mengenai tren "
        "perdagangan (trading strategies)."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


def download_economy_dataset() -> dict[str, Any]:
    """Download dataset Economy."""
    hf_id = "teknium/dataforge-economics"
    system_prompt = (
        "Kamu adalah Economy Agent. Tugasmu adalah melakukan simulasi ekonomi, "
        "menganalisis data makroekonomi, dan membuat prediksi tren ekonomi global."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


def download_education_dataset() -> dict[str, Any]:
    """Download dataset Education."""
    hf_id = "ASSISTments/FoundationalASSIST"
    system_prompt = (
        "Kamu adalah Education Agent. Tugasmu adalah membantu sistem pembelajaran "
        "adaptif, knowledge tracing, dan memberikan bimbingan belajar (tutoring) "
        "personal kepada siswa."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


def download_entertainment_dataset() -> dict[str, Any]:
    """Download dataset Entertainment."""
    hf_id = "krishnakamath/movielens-32m-movies-enriched-with-SIDs"
    system_prompt = (
        "Kamu adalah Entertainment Agent. Tugasmu adalah merekomendasikan film, "
        "memahami preferensi hiburan, dan memberikan personalisasi konten."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


def download_mathematics_dataset() -> dict[str, Any]:
    """Download dataset Mathematics."""
    hf_id = "hoskinson-center/proof-pile"
    system_prompt = (
        "Kamu adalah Mathematics Agent. Tugasmu adalah memecahkan persoalan matematika, "
        "membuktikan teorema, dan memanipulasi komputasi simbolik."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


def download_science_dataset() -> dict[str, Any]:
    """Download dataset Science."""
    hf_id = "graphs-datasets/QM9"
    system_prompt = (
        "Kamu adalah Science Agent. Tugasmu adalah membantu desain eksperimen, "
        "menganalisis struktur molekuler (QM9), dan melakukan penambangan "
        "literatur sains."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


def download_healthcare_dataset() -> dict[str, Any]:
    """Download dataset Healthcare."""
    hf_id = "starmpcc/Asclepius-Synthetic-Clinical-Notes"
    system_prompt = (
        "Kamu adalah Healthcare Agent spesialis catatan klinis. Tugasmu adalah "
        "menganalisis gejala medis, mengekstrak entitas kesehatan dari catatan medis, "
        "dan mengecek interaksi obat."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


def download_legal_dataset() -> dict[str, Any]:
    """Download dataset Legal."""
    hf_id = "cuad"
    system_prompt = (
        "Kamu adalah Legal Agent. Tugasmu adalah memahami bahasa hukum, "
        "menganalisis klausul dalam kontrak (CUAD), dan melakukan compliance checking."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


def download_cybersecurity_dataset() -> dict[str, Any]:
    """Download dataset Cybersecurity."""
    hf_id = "argilla/cybersecurity-incidents"
    system_prompt = (
        "Kamu adalah Cybersecurity Agent. Tugasmu adalah mendeteksi anomali keamanan, "
        "mengklasifikasikan insiden ancaman siber, dan merekomendasikan perlindungan."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


def download_creative_dataset() -> dict[str, Any]:
    """Download dataset Creative."""
    hf_id = "huggan/wikiart_info"
    system_prompt = (
        "Kamu adalah Creative & Design Agent. Tugasmu adalah memahami gaya seni rupa, "
        "membantu brainstorming desain, dan merakit ide-ide kreatif untuk prompt gambar."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


def download_devops_dataset() -> dict[str, Any]:
    """Download dataset DevOps."""
    hf_id = "marmikpandya/devops-QA"
    system_prompt = (
        "Kamu adalah DevOps & Infrastructure Agent. Tugasmu adalah memberikan "
        "rekomendasi CI/CD, memecahkan masalah konfigurasi Docker/K8s, dan "
        "membantu otomatisasi server."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


def download_data_engineering_dataset() -> dict[str, Any]:
    """Download dataset Data Engineering."""
    hf_id = "gretelai/synthetic_text_to_sql"
    system_prompt = (
        "Kamu adalah Data Engineering Agent. Tugasmu adalah menulis pipeline ETL, "
        "merancang struktur query (Text-to-SQL), serta membersihkan dan "
        "menormalkan data mentah."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


def download_osint_dataset() -> dict[str, Any]:
    """Download dataset OSINT."""
    hf_id = "cc_news"
    system_prompt = (
        "Kamu adalah OSINT Agent. Tugasmu adalah menganalisis data artikel publik, "
        "melacak tren berita global, melakukan fact-checking, dan meringkas isu terkini."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


def download_game_ai_dataset() -> dict[str, Any]:
    """Download dataset Game AI."""
    hf_id = "Zarroc/lichess-historic-data"
    system_prompt = (
        "Kamu adalah Game AI Agent. Tugasmu adalah menganalisis histori permainan catur, "
        "mempelajari taktik NPC, dan merancang logika game balancing serta konten prosedural."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


def download_productivity_dataset() -> dict[str, Any]:
    """Download dataset Productivity."""
    hf_id = "enron_emails"
    system_prompt = (
        "Kamu adalah Productivity Agent (Executive Assistant). Tugasmu adalah "
        "merangkum korespondensi email, membantu memprioritaskan kalender tugas, "
        "dan mengatur alur kerja harian."
    )
    dataset = load_dataset(hf_id)
    return {"dataset": dataset, "huggingface_id": hf_id, "system_prompt": system_prompt}


# Mendaftarkan fungsi dan deskripsi ke dalam Registry Global
_DOMAIN_REGISTRY: dict[str, dict[str, Any]] = {
    "nlp": {
        "function": download_nlp_dataset,
        "description": "WhatsApp Intent Classification / Customer Support",
    },
    "finance": {
        "function": download_finance_dataset,
        "description": "Financial News Sentiment Analysis",
    },
    "economy": {
        "function": download_economy_dataset,
        "description": "Dataforge Economics & Macro Data",
    },
    "education": {
        "function": download_education_dataset,
        "description": "ASSISTments Knowledge Tracing",
    },
    "entertainment": {
        "function": download_entertainment_dataset,
        "description": "MovieLens Recommendations Enriched",
    },
    "mathematics": {
        "function": download_mathematics_dataset,
        "description": "Proof Pile Theorem Pairs",
    },
    "science": {
        "function": download_science_dataset,
        "description": "QM9 Molecular Properties",
    },
    "healthcare": {
        "function": download_healthcare_dataset,
        "description": "Asclepius Synthetic Clinical Notes",
    },
    "legal": {
        "function": download_legal_dataset,
        "description": "CUAD Legal Clause Analysis",
    },
    "cybersecurity": {
        "function": download_cybersecurity_dataset,
        "description": "Cybersecurity Incident Detection",
    },
    "creative": {
        "function": download_creative_dataset,
        "description": "WikiArt Information & Design",
    },
    "devops": {
        "function": download_devops_dataset,
        "description": "DevOps QA & Pipeline Data",
    },
    "data_engineering": {
        "function": download_data_engineering_dataset,
        "description": "Synthetic Text to SQL Pipeline",
    },
    "osint": {
        "function": download_osint_dataset,
        "description": "CC News Open-Source Articles",
    },
    "game_ai": {
        "function": download_game_ai_dataset,
        "description": "Lichess Historic Data Analytics",
    },
    "productivity": {
        "function": download_productivity_dataset,
        "description": "Enron Emails Productivity Summarization",
    },
}

if __name__ == "__main__":
    # Contoh penggunaan untuk satu domain
    print("Mencoba memuat metadata dataset NLP...")
    result = _DOMAIN_REGISTRY["nlp"]["function"]()
    print(f"Agent Prompt : {result['system_prompt']}")
    print(f"HF Dataset ID: {result['huggingface_id']}")
    print(f"Dataset      : {result['dataset']}")
