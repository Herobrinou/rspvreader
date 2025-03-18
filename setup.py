from setuptools import setup, find_packages

setup(
    name="speedreader",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "customtkinter>=5.2.2",
        "pyttsx3>=2.90",
        "pillow>=10.0.0",
        "darkdetect>=0.8.0",
        "packaging>=24.1"
    ],
    entry_points={
        'console_scripts': [
            'speedreader=src.speedreader:main',
        ],
    },
    author="Brinou",
    author_email="",
    description="Speed Reader Pro - A modern speed reading application with text-to-speech support",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords="speed reading, text-to-speech, reading assistant",
    url="",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Education",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
) 