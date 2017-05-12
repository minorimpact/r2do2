
import logging
import os
import sys

sys.path.insert(0, '/home/pgillan/dev/r2do2')
logging.basicConfig(stream=sys.stderr)

os.environ['R2DO2_DB_PASSWORD'] = 'ourtodotoo'
os.environ['R2DO2_DB_SERVER'] = 'db.minorimpact.com'

from app import app as application
