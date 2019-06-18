from setuptools import setup, PEP420PackageFinder

setup(
    name="pygrid",
    packages=PEP420PackageFinder.find("src"),
    package_dir={"": "src"},
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=["toml", "networkx"],
    extras_require={
        "testing": ["pytest", "pytest-mock"],
        "documentation": ["sphinx", "sphinx_rtd_theme", "sphinx-autobuild", "sphinxcontrib-napoleon"],
    },
    zip_safe=False,
)
