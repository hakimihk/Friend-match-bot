# Procfile — Used by Railway, Render, Heroku
# Runs the bot in webhook mode using Gunicorn

web: gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 wsgi:app
