## Smart Cams

### Setup:
```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
# enter the details
python manage.py runserver
# visit localhost:8000/
# For admin dashboard visit localhost:8000/admin and enter the credentials
```

**Note:** Use `python3` command instead of `python` if your `python` comamand doesn't mean python3.x
 
# TODO: 

- Refactor recorder script and make it multi-threaded with [this](https://nrsyed.com/2018/07/05/multithreading-with-opencv-python-to-improve-video-processing-performance/)