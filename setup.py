from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='dungeonmaker',
    version='0.6.13',
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
        'Programming Language :: Python :: 3.11',
    ],
    keywords=['scratch'],
    install_requires=[
        'scratchcommunication',
        'pymongo',
        'scratchattach',
    ],
    python_requires='>=3.11',
)