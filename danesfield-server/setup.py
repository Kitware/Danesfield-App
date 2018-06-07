import re
from setuptools import setup, find_packages

requires = []
dep_links = []
# parse requirements file
with open('requirements.txt') as f:
    comment = re.compile('(^#.*$|\s+#.*$)')
    for line in f.readlines():
        line = line.strip()
        line = comment.sub('', line)
        if line:
            if line.startswith('git+') and '#egg=' in line:
                dep_links.append(line)
                requires.append(line.split('#egg=', 1)[1].replace('-', '=='))
            else:
                requires.append(line)

setup(name='danesfield-server',
      version='0.0.0.dev1',
      description='',
      url='',
      install_requires=requires,
      dependency_links=dep_links,
      author='Kitware Inc',
      author_email='',
      license='',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: OSI Approved :: Apache Software License'
          'Topic :: Scientific/Engineering :: GIS',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Programming Language :: Python'
      ],
      packages=find_packages(exclude=['tests*', 'server*', 'docs']),
      zip_safe=False)
