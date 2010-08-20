from setuptools import setup
setup(name="mudmate",
        package_dir={ "": "lib" },
        packages=[
            "mudmate",
            "mudmate.core",
            "mudmate.config",
            "mudmate.events",
            "mudmate.modules",
            "mudmate.modules.mapper",
            ],
        version="0.1",
        )
