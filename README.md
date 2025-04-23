> 🔽 Note: `dashboard_ai_tagged.csv` is compressed as `dashboard_ai_tagged_slim.csv.gz` for performance.  
> To load:
```python
import pandas as pd
df = pd.read_csv("data/dashboard_ai_tagged_slim.csv.gz", compression='gzip')
