# Ordering service API
Order automation for the retail chain. Users of the service are the buyer (the manager of the retail chain, who purchases products for sale in the store) and the supplier of products.

## Get frome source
```shell
  git clone git@github.com:ilya-goldin/ordering-service-api.git

  cd ordering-service-api

  pip install --upgrade pip

  pip install -r requirements.txt

  python manage.py makemigrations
 
  python manage.py migrate

  python manage.py createsuperuser 
```

## Tests coverage
![Tests coverage screenshot](static/Screenshot%20from%202021-11-14%2018-08-04.png)