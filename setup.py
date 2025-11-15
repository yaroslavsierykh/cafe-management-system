from setuptools import setup, find_packages

setup(
    name='cafe-management',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask==3.0.2',
        'flask-sqlalchemy',
        'flask-login',
        'werkzeug'
    ]
) 