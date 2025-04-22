> 🔽 Note: `dashboard_ai_tagged.csv` is compressed as `dashboard_ai_tagged.csv.gz` for performance.  
> To load:
```python
import pandas as pd
df = pd.read_csv("data/dashboard_ai_tagged.csv.gz", compression='gzip')
