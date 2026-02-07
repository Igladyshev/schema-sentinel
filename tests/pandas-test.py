from datetime import datetime

import pandas as pd

now = datetime.now()
df = pd.DataFrame(
    [("ANALYTICS_DB", "DB_ADMIN", "FALSE", "Analytics Database", now, now, 30)],
    ["database_name", "database_owner", "is_transient", "created", "last_altered", "retention_period"],
)
