# ![gMemegen](https://github.com/GoogleCloudPlatform/gmemegen/raw/master/app/static/images/gmemegen.png)
[![CircleCI](https://circleci.com/gh/GoogleCloudPlatform/gmemegen.svg?style=svg)](https://circleci.com/gh/GoogleCloudPlatform/gmemegen)

**Notice:** this project has been archived and is no longer being maintained. 

gMemegen is a sample application, showcasing Cloud SQL Postgres connectivity from a Kubernetes
cluster running on Google Kubernetes Engine. 


## Deployment
You can find the complete instructions (including resource setup) in the form a codelab, located 
[here](https://codelabs.developers.google.com/codelabs/cloud-postgresql-gke-memegen). 

The app attempts a connection to a postgres server located at 127.0.0.1 unless otherwise specificed.
For a full list of available flags, use `python app/main.py -help`.

### Local deployment

Install the requirements (inside a [virtualenv](https://virtualenv.pypa.io/en/stable/userguide/))
```bash
pip install -r app/requirements.txt
```

With [cloud_sql_proxy](https://cloud.google.com/sql/docs/mysql/sql-proxy) running, start the 
application on the debug server: 
```bash
python app/main.py --DB_USER <db_user> --DB_PASS <db_pass>
```

Verify the app is running by navigating to [http://127.0.0.1:5000](http://127.0.0.1:5000).

Use `Ctrl+C` to stop the application at any time.

### Local deployment inside Docker:

Build the docker with:
```bash
docker build -t gmemegen .
```

With [cloud_sql_proxy](https://cloud.google.com/sql/docs/mysql/sql-proxy) running, start the 
container:
```bash
docker run  --net="host" -it --rm --name runtime -e "DB_PASS=1qaz2wsx" gmemegen
```

Verify the app is running by navigating to [http://127.0.0.1:5000](http://127.0.0.1:5000).

Use `Ctrl+C` to stop the application at any time.

### Kubernetes Deployment

Create a kubernetes secret named `cloudsql-instance-credentials` from your service account key:
```bash
kubectl create secret generic cloudsql-instance-credentials \
    --from-file=credentials.json=service_account_key.json
```

Create a kubernetes secret named `cloudsql-db-credentials` from your database credentials key:
```bash
kubectl create secret generic cloudsql-db-credentials \
    --from-literal=username=[DB_USER] \
    --from-literal=password=[DB_PASS]
```

Update the `gmemegen_deployment.yaml` by replacing variables in the following sections:
* `gcr.io/[PROJECT_ID]/gmemegen` with the correct project name.
* `"-instances=<INSTANCE_CONNECTION_NAME>=tcp:5432"` with your Cloud SQL connection name.

Create your deployment on your cluster:
```bash
kubectl create -f gmemegen_deployment.yaml
``` 

To access your deployment via the web, expose it with a `LoadBalancer` object:
```bash
kubectl expose deployment gmemegen --type "LoadBalancer" --port 80 --target-port 8080
```

After 2-3 minutes, describe the service to find the `"LoadBalancer Ingress"`.
```$xslt
kubectl describe services gmemegen
```

Your service should be ready at http://[LoadBalancer Ingress]:80. Navigate to your URL and make some
 memes!

## Disclaimer

This is not an official Google product.
