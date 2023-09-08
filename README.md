# Axolotl 

<img src="resources/images/axolotl.png" align="center" width="256">

 

 # 

# db utils

## install
```bash
pip install axolotl-dbu
```

## dev install 
```bash
pip install -e ./
cp example.env .env
```

# cli help
```bash
axolotl --help 
axolotl backup-and-restore --help
axolotl db-utils --help
```
# config file
create a axolotl-clusters.yml file in the /.config
directory in your home

## cluster config file
```yml
local: mongodb://localhost:27017
beta: mongodb+srv://<user>:<password>@some-cluster.mongodb.net/
```

## move db form one cluster to another

```bash
axolotl db-utils move-db-cluster -oc beta -dc local -db jokes -p ./tmp
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
```