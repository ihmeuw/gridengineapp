from setuptools import setup, PEP420PackageFinder

setup(
    name="gridengineapp",
    packages=PEP420PackageFinder.find("src"),
    package_dir={"": "src"},
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=["toml", "networkx"],
    extras_require={
        # You might put these in tests_require if you are using
        # setup.py, but pip wants them here.
        "testing": ["pytest", "pytest-mock", "pandas", "tables"],
        "documentation": ["sphinx", "sphinx_rtd_theme", "sphinx-autobuild", "sphinxcontrib-napoleon"],
    },
    zip_safe=False,
)
