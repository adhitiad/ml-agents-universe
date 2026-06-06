import os
import textwrap

HF_REGISTRY = {
    "nlp": ("bitext/Bitext-customer-support-llm-chatbot-training-dataset", "Kamu adalah NLP Agent. Tugasmu memproses bahasa natural, menganalisis sentimen, dan mendukung chatbot."),
    "finance": ("zeroshot/twitter-financial-news-sentiment", "Kamu adalah Finance Agent. Tugasmu menganalisis berita keuangan dan tren sentimen pasar."),
    "economy": ("teknium/dataforge-economics", "Kamu adalah Economy Agent. Tugasmu melakukan simulasi ekonomi dan menganalisis makroekonomi global."),
    "education": ("NahedAbdelgaber/evaluating-student-writing", "Kamu adalah Education Agent. Tugasmu membantu sistem pembelajaran adaptif dan knowledge tracing."),
    "entertainment": ("krishnakamath/movielens-32m-movies-enriched-with-SIDs", "Kamu adalah Entertainment Agent. Tugasmu merekomendasikan film dan personalisasi konten."),
    "mathematics": ("TIGER-Lab/MathInstruct", "Kamu adalah Mathematics Agent. Tugasmu memecahkan persoalan matematika dan komputasi simbolik."),
    "science": ("lisn519010/QM9", "Kamu adalah Science Agent. Tugasmu membantu desain eksperimen dan menganalisis struktur molekuler."),
    "healthcare": ("starmpcc/Asclepius-Synthetic-Clinical-Notes", "Kamu adalah Healthcare Agent. Tugasmu mengekstrak entitas kesehatan dari catatan medis."),
    "legal": ("nguha/legal_mcq", "Kamu adalah Legal Agent. Tugasmu menganalisis klausul dalam kontrak legal."),
    "cybersecurity": ("Trendyol/Trendyol-Cybersecurity-Instruction-Tuning-Dataset", "Kamu adalah Cybersecurity Agent. Tugasmu mengklasifikasikan insiden ancaman siber."),
    "creative": ("huggan/wikiart", "Kamu adalah Creative Agent. Tugasmu memahami metadata seni rupa dan merakit ide kreatif."),
    "devops": ("RazinAleks/SO-Python_QA-System_Administration_and_DevOps_class", "Kamu adalah DevOps Agent. Tugasmu memecahkan masalah konfigurasi dan CI/CD."),
    "data_engineering": ("gretelai/synthetic_text_to_sql", "Kamu adalah Data Engineering Agent. Tugasmu merancang query Text-to-SQL dan pipeline ETL."),
    "osint": ("SetFit/ag_news", "Kamu adalah OSINT Agent. Tugasmu melacak tren berita global dan fact-checking."),
    "game_ai": ("mateuszgrzyb/lichess-stockfish-normalized", "Kamu adalah Game AI Agent. Tugasmu menganalisis histori permainan catur dan taktik."),
    "productivity": ("SetFit/enron_spam", "Kamu adalah Productivity Agent. Tugasmu merangkum email dan mengatur prioritas tugas kerja.")
}

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agents"))

for domain, (hf_id, prompt) in HF_REGISTRY.items():
    # 1. OPTIMASI: Simpan Prompt di folder Configs, bukan di Data
    config_dir = os.path.join(base_path, domain, 'configs')
    os.makedirs(config_dir, exist_ok=True)
    with open(os.path.join(config_dir, 'system_prompt.txt'), 'w', encoding='utf-8') as f:
        f.write(prompt)
        
    data_dir = os.path.join(base_path, domain, 'src', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    with open(os.path.join(data_dir, '__init__.py'), 'w') as f:
        f.write('')
        
    dataset_file = os.path.join(data_dir, 'dataset.py')
    func_name = f'download_{domain}_dataset'
    
    code = textwrap.dedent(f'''\
        import os
        from pathlib import Path
        import polars as pl
        import logging

        logger = logging.getLogger(__name__)

        try:
            from datasets import load_dataset
        except ImportError:
            raise ImportError("Harap jalankan: pip install datasets pyarrow polars")
        
        def {func_name}(**kwargs) -> Path:
            """Download HuggingFace dataset untuk domain {domain}."""
            # Ambil Token HF dari environment (berguna untuk dataset private/gated)
            hf_token = os.environ.get("HF_TOKEN")
            
            data_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "raw", "{domain}")))
            data_dir.mkdir(parents=True, exist_ok=True)
            
            output_path = data_dir / "{domain}_dataset.parquet"
            
            force_clean = kwargs.get("force", False)
            is_full = kwargs.get("full", False)
            
            if not output_path.exists() or force_clean:
                logger.info(f"Mengunduh dataset {hf_id} dari HuggingFace...")
                
                # Mengunduh dataset tanpa trust_remote_code
                ds = load_dataset("{hf_id}", token=hf_token)
                
                if hasattr(ds, "keys"):
                    split_name = "train" if "train" in ds.keys() else list(ds.keys())[0]
                    ds = ds[split_name]
                    
                if not is_full and len(ds) > 1000:
                    ds = ds.select(range(1000))
                    
                # OPTIMASI: Konversi via PyArrow agar 100% kompatibel dengan Polars DataFrame
                # Menghindari error tipe data kompleks (nested json/list)
                try:
                    df = pl.from_arrow(ds.data.table)
                    df.write_parquet(str(output_path))
                except Exception as e:
                    logger.warning(f"Gagal konversi native arrow. Fallback ke Pandas: {{e}}")
                    df = pl.from_pandas(ds.to_pandas())
                    df.write_parquet(str(output_path))
                
            return output_path
        ''')
        
    with open(dataset_file, 'w', encoding='utf-8') as f:
        f.write(code)

print("✅ Generasi file dataset.py berhasil dengan standar Production-Ready!".encode('cp1252', errors='replace').decode('cp1252'))
