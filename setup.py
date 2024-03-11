from setuptools import setup, find_packages

setup(
    name="ecl-dev-tools",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyModbusTCP",
        "millify",
        "tableprint"
    ],
    entry_points={
        'console_scripts': [
            'solaxtop = solaxtools.solaxtop:solaxtop',
        ]
    }
)