from alembic.config import Config
from alembic import command
import os

here = os.path.abspath(os.path.dirname(__file__))
config = Config(os.path.join(here, 'alembic.ini'))
# ensure script_location is correct
config.set_main_option('script_location', os.path.join(here, 'alembic'))

if __name__ == '__main__':
    command.upgrade(config, 'head')
