import sys
sys.path.insert(0, '.')
from storage.results_db import engine
from sqlalchemy import text

with engine.begin() as conn:
    for op in ['_insert', '_read', '_update', '_delete', '_query']:
        conn.execute(text(f"UPDATE benchmark_results SET scenario_name = REPLACE(scenario_name, '{op}', '') WHERE scenario_name LIKE '%{op}'"))

print('Database history cleaned!')
