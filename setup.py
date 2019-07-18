from setuptools import setup, PEP420PackageFinder

setup(
    name="gridengineapp",
    author="IHME, University of Washington",
    author_email="adolgert@uw.edu",
    description=("An application framework for writing "
                 "Grid Engine applications"),
    url="https://gridengineapp.readthedocs.io/en/latest",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
    ],
    packages=PEP420PackageFinder.find("src"),
    package_dir={"": "src"},
    package_data={"gridengineapp": [
        "configuration.cfg",
    ]},
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=["networkx"],
    extras_require={
        # You might put these in tests_require if you are using
        # setup.py, but pip wants them here.
        "testing": ["pytest", "pytest-mock", "pandas", "tables"],
        "documentation": [
            "sphinx",
            "sphinx_rtd_theme",
            "sphinx-autobuild",
            "sphinxcontrib-napoleon",
        ],
    },
    zip_safe=False,
)
