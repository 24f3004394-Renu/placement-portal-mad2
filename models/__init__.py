from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from .admin import Admin
from .company import Company
from .student import Student
from .drive import PlacementDrive
from .application import Application
from .placement import Placement
from .interview import Interview