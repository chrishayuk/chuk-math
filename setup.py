from setuptools import setup, find_packages

setup(
    name="your_app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        're',
        'langchain',
        'langchain-ollama'
    ],
    entry_points={
        'console_scripts': [
            'your_app=your_module.main:main',
        ],
    },
    author="Your Name",
    author_email="your_email@example.com",
    description="A brief description of your app",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/your_app",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)