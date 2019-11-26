from setuptools import setup, find_packages

setup(
    name='subtools',
    version='0.1',
    packages=find_packages(),
    # package_dir={'subtools': 'src'},
    url='https://github.com/iisharankov/Effelsberg/',
    license='',
    entry_points={
        "console_scripts": [
            "subreflector_program = subtools.subreflector_start_server:main",
            "subreflector_mockserver = subtools.mock_start_server:main",
            ]},
    author='Ivan Sharankov',
    author_email='ivansharankov3@gmail.com',
    description='Hexapod Tools',
    zip_safe=False,
)
