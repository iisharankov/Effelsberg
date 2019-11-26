from setuptools import setup, find_packages

setup(
    name='subtools',
    version='0.1',
    packages= find_packages(),
    # package_dir={'subtools': 'src'},
    url='https://github.com/iisharankov/Effelsberg/',
    license='',
    entry_poimts={
        "console_scripts": ["subreflector_program=subtools:main"]
    },
    author='Ivan Sharankov',
    author_email='ivansharankov3@gmail.com',
    description='Hexapod Tools',
    zip_safe=False,
)
