from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='dungeonmaker',
    version='0.3.1',
    author='Simon Gilde',
    author_email='simon.c.gilde@gmail.com',
    description='Dungeon maker backend and other things',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/thecommcraft/dungeon-maker-reinvented',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords=['scratch'],
    install_requires=[
        'scratchcommunication',
        'pymongo'
    ],
    python_requires='>=3.10',
)