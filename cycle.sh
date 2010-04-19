export PYTHONPATH="$PYTHONPATH:/var/www/youvj.com:."; kill `cat twistd.pid`; twistd -y vidserv.py
