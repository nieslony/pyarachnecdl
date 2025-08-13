from setuptools import setup
# import src.arachne_dbus as arachne_dbus

setup(
    name = "pyarachnecdl",
    description = "Arachne Config Downloader",
    version = "1.4.0",
    author = "Claas Nieslony",
    license = "GPLv3",
    packages = ["pyarachnecdl"],
    package_dir = {
        "": "src"
        },
    entry_points = {
        'console_scripts': [
            'pyarachnecdl = pyarachnecdl.arachne_config_downloader:main',
        ],
    },
    package_data={
        "pyarachnecdl": ["data/*svg"],
    },
    install_requires=[
          "pyqt6",
          "requests",
          "requests-kerberos",
          "dbus-python"
    ],
)
