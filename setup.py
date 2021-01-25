from distutils.core import setup
import sys

packages = ['aani', 'aani.resources']
install_requires = ["markdown", "pyhtml"]

setup(name='Aani',
      version='0.1',
      author='Felix G. Knorr',
      author_email='knorr.felix@gmx.de',
      packages=packages,
      install_requires=install_requires,
      entry_points = {
        'console_scripts': ['aani=aani.aani:cli']
      },                                                                                                            
      include_package_data=True,                                                                                    
      python_requires='>=3.7') 
