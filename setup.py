from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()
    
setup(name="topaspy",
      author="Tom Wood",
      author_email="thomas.wood@stfc.ac.uk",
      maintainer="Tom Wood",
      maintainer_email="thomas.wood@stfc.ac.uk",
      description="topaspy: Python frontend for TOPAS refinement program",
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=find_packages(),
      install_requires=['pymatgen'],
      extras_require={'tests': ['pytest', 'pytest-cov']}
      )
