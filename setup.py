import setuptools

setuptools.setup(
    name="hippo_gym",
    version="2.0.0a",
    description="Human Input Parsing Platform for OpenAI Gym",
    author="Nick Nissen",
    author_email="nnissen@ualberta.ca",
    install_requires=[
        "shortuuid>=1.0.1",
        "asyncio>=3.4.3",
        "websockets>=9.1",
        "numpy>=1.18.5",
        "Pillow>=8.2.0",
        "boto3>=1.14.20",
        "python-dotenv>=0.14.0",
        "pyYaml>=5.4",
    ],
    url="https://hippogym.irll.net",
    license="MIT",
    packages=setuptools.find_packages(),
)
