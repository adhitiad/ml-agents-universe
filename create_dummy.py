import os
import textwrap

domains = ['healthcare', 'legal', 'cybersecurity', 'creative', 'devops', 'data_engineering', 'osint', 'game_ai', 'productivity']
base_path = 'e:/dev/ml-agents-universe/agents'

for domain in domains:
    data_dir = os.path.join(base_path, domain, 'src', 'data')
    os.makedirs(data_dir, exist_ok=True)
    init_file = os.path.join(data_dir, '__init__.py')
    with open(init_file, 'w') as f:
        f.write('')
        
    dataset_file = os.path.join(data_dir, 'dataset.py')
    func_name = f'download_{domain}_dataset'
    
    with open(dataset_file, 'w') as f:
        f.write(textwrap.dedent(f'''\
        import os
        from pathlib import Path
        import polars as pl
        
        def {func_name}(**kwargs) -> Path:
            """Download dummy dataset for {domain}."""
            data_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "raw", "{domain}")))
            data_dir.mkdir(parents=True, exist_ok=True)
            
            output_path = data_dir / "dummy_data.parquet"
            
            if not output_path.exists() or kwargs.get("force", False):
                # Create dummy data
                df = pl.DataFrame({{
                    "id": range(1, 101),
                    "feature": [f"{domain}_feat_{{i}}" for i in range(1, 101)],
                    "label": [i % 5 for i in range(1, 101)]
                }})
                df.write_parquet(output_path)
                
            return output_path
        '''))
        
print('Dataset downloaders created.')
