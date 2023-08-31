# Axolotl 

<img src="resources/images/axolotl.png" align="center" width="256">
 

 # 

# db utils
```bash
pip install ./
cp example.env .env
```

# cli help
```bash
axolotl --help 
axolotl backup-and-restore --help
axolotl db-utils --help
```


# example
```python
import os
import dotenv
from axolotl import BackupAndRestoreClient

dotenv.load_dotenv()

client = BackupAndRestoreClient(db_uir=os.getenv("MONGO_DB_URI"))
client.backup_collection(
    db="jokes", collection="funny-jokes", path="./results"
)



