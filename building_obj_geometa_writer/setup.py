from setuptools import setup

setup(
    name='girder-plugin-geometa-obj',
    author='Kitware, Inc.',
    entry_points={
        'geometa.types': [
            'vector=building_obj.schema:handler'
        ]
    },
    packages=[
        'building_obj'
    ],
    install_requires=[
        # Eventually will require geometa girder plugin
        # as a dependency here
    ]
)
