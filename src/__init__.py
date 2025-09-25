"""
HVDC Project - Samsung C&T Logistics & ADNOC-DSV Partnership
MACHO-GPT v3.4-mini for Advanced Logistics AI System
"""

__version__ = "3.4.0"
__author__ = "MACHO-GPT Team"
__description__ = "HVDC Project Logistics AI System"
__package__ = "src"

# Core modules
from . import models
from . import services  
from . import utils
from . import apis

__all__ = [
    "models",
    "services", 
    "utils",
    "apis",
    "__version__",
    "__author__",
    "__description__"
]
