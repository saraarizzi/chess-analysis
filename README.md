### Project setup steps
 
1. Install libraries used in the project

```shell
pip install -r requirements.txt
```

2. Set environment variables to connect to MongoDB and Neo4j

```python
import os

# used to connect to MongoDB
os.setenv("MONGO_HOST", "<insert-value-provided>")
os.setenv("MONGO_USER", "<insert-value-provided>")
os.setenv("MONGO_PSW", "<insert-value-provided>")

# used to connect to Neo4j
os.setenv("NEO_HOST", "<insert-value-provided>")
os.setenv("NEO_USER", "<insert-value-provided>")
os.setenv("NEO_PSW", "<insert-value-provided>")
```

3. Airflow installation

```shell
export AIRFLOW_HOME=<insert-your-pwd> 
pip install apache-airflow
airflow db init
airflow webserver
airflow scheduler
```

