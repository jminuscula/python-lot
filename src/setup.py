from distutils.core import setup

setup(
    name="lot",
    packages=["lot"],
    version="0.1.0",
    description="light over twitter",
    author="Jacobo Tarragón",
    author_email="jacobo.tarragon@gmail.com",

    scripts=['bin/lot.py', 'bin/lot-setup-credentials.py'],
    data_files=[('/etc/init.d', ['bin/lot'])]

    url="https://github.com/jminuscula/python-lot",
    keywords=["raspberry pi", "hardware", "twitter"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Telecomunications Industry",
        "Intended Audience :: Information Technology",
    ],
    long_description=("Library to build a pair of synchronizating lights "
                      "controlled by Raspberry Pis and communicating via "
                      "Twitter"),
)