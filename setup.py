from setuptools import setup, find_packages

setup(
    name="BasketBot",
    version="0.0.1",
    packages=find_packages(),
    description = "Aggregating local basket prices",
    python_requires='>=3',
    # scripts = ["scripts/fs"],
    author = "Nic",
    author_email = "sparrigan@gmail.com",
    url = "https://github.com/sparrigan/BasketBot",
    # setup_requires = DEPENDENCIES,
    # install_requires = DEPENDENCIES,
    include_package_data = True
)
