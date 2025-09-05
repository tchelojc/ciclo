from setuptools import setup, find_packages

setup(
    name="calendario_maya",
    version="1.0.0",
    packages=find_packages(include=["calendario_maya", "calendario_maya.*"]),
    include_package_data=True,
    package_data={
        'calendario_maya': ['data/*.json', 'interface/assets/*'],
    },
    install_requires=[
        'PyQt6>=6.0.0',
        'numpy>=1.20.0',
        'pyephem>=4.1.0',
    ],
    python_requires='>=3.8',
)
