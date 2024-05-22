from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in ecommerce_business_store_singlevendor/__init__.py
from ecommerce_business_store_singlevendor import __version__ as version

setup(
	name="ecommerce_business_store_singlevendor",
	version=version,
	description="Single vendor ecommerce app",
	author="Tridotstech Private Ltd.",
	author_email="info@valiantsystems.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
