from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='vinews',
    version='0.1.0-beta.3',
    install_requires=requirements,
    include_package_data=True,
    packages=find_packages(exclude=['tests', 'tests.*']),
    author='Kiet Do',
    author_email="kietdohuu@gmail.com",
    description='Vinews is an open-source library which provides modules for searching and scraping news data from Vietnamese news websites.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    keywords='news, scraping, vietnamese, vietnam, web scraping, news scraping',
    python_requires='>=3.12',
    url='https://github.com/JustKiet/vinews',
    project_urls={
        'Bug Reports': 'https://github.com/JustKiet/vinews/issues',
        'Source': 'https://github.com/JustKiet/vinews',
        'Documentation': 'https://github.com/JustKiet/vinews#readme',
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: Python :: 3.15',
        'Topic :: Software Development :: Libraries',
    ],
)