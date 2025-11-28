import sys
import os

# Add project directory to path
path = '/home/muratcankoptay/tevkil_proje'
if path not in sys.path:
    sys.path.append(path)

# Activate virtual environment
virtualenv_path = '/home/muratcankoptay/tevkil_proje/venv'
activate_this = os.path.join(virtualenv_path, 'bin', 'activate_this.py')

# Python 3.11+ için activate_this.py yoksa alternatif
if os.path.exists(activate_this):
    exec(open(activate_this).read(), dict(__file__=activate_this))
else:
    # Modern Python için
    import site
    site.addsitedir(os.path.join(virtualenv_path, 'lib', 'python3.11', 'site-packages'))

# Import Flask app
from app import app as application
