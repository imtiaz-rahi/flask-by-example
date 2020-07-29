# flask-by-example
Learning project following the article at RealPython

- https://realpython.com/learning-paths/flask-by-example/
- https://realpython.com/flask-by-example-part-1-project-setup/

```bash
# For staging environment on heroku
$ git push stage master
$ heroku run python app.py --app wordcount-ir-beta

# For production environment on heroku
$ git push prod master
$ heroku run python app.py --app wordcount-ir-prod
```

### Database Management ###
```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

```
heroku config --app wordcount-ir-beta
heroku addons:create heroku-postgresql:hobby-dev --app wordcount-ir-beta
heroku run python manage.py db upgrade --app wordcount-ir-beta
```

heroku addons:docs heroku-postgresql        # to view documentation

