from .base import *

# Import dev or prod based on environment
import os
env = os.environ.get('DJANGO_ENV', 'dev')
if env == 'production':
    from .prod import *
else:
    from .dev import *
