import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Impianto termoregolazione",
    version="0.0.1",
    author="Alessandro Oniarti",
    author_email="onniale@gmail.com",
    description="Impianto ioT per la termoregolazione e la sensoristica",
    url="https://github.com/Onni97/ImpiantoTermoregolazionePython",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
)