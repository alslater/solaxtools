from setuptools import setup, find_packages

setup(
    name="solaxtools",
    version="0.7",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "influxdb",
        "millify",
        "python-daemon",
        "pid",
        "pyModbusTCP",
        "tableprint",
        "requests"
    ],
    entry_points={
        'console_scripts': [
            'solaxtop = solaxtools.solaxtop:solaxtop',
            'solax2influxdb = solaxtools.solax_to_influxdb:run',
        ]
    }
)
