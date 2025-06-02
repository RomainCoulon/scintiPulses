from setuptools import setup, find_packages
import codecs
import os

VERSION = "1.13"

DESCRIPTION = "scintiPulses"

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name = "scintiPulses",
    version = VERSION,
    author = "RomainCoulon (Romain Coulon)",
    author_email = "<romain.coulon@bipm.org>",
    description = DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/scintiPulses/",
    py_modules=['scintiPulses'],
    project_urls={'Documentation': 'https://github.com/RomainCoulon/scintiPulses/',},
    packages = find_packages(),
    install_requires = ["numpy","scipy"],
    python_requires='>=3.11',
    keywords = ["Python","scintillation","quantum illumination function","particle physics", "signal", "simulation"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Natural Language :: French",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Scientific/Engineering :: Physics",
    ],
#    include_package_data = True,
#    package_data = {'': [
#	    	#'decayData/All-nuclides_PenNuc.zip',
#		]},
)
