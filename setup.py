from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.31'
DESCRIPTION = 'Automating video and short content creation with AI'
LONG_DESCRIPTION = 'A powerful tool for automating content creation. It simplifies video creation, footage sourcing, voiceover synthesis, and editing tasks.'


setup(
    name="shortgpt",
    version=VERSION,
    author="RayVentura",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    package_data={'': ['*.yaml', '*.json']},    # This will include all yaml files in package
    install_requires=[
        'python-dotenv',
        'openai==1.37.0',
        'httpx==0.27.2',
        'tiktoken',
        'PyYAML>=6.0.1',  # For YAML file handling
        'tinydb',
        'pymongoarrow>=1.0.0',  # Instead of tinymongo
        'proglog',
        'yt-dlp>=2025.1.12',
        'torch',
        'torchaudio',
        'srt==3.5.3',  # Required by whisper-timestamped
        'whisper-timestamped',
        'protobuf==3.20.3',
        'pillow>=9.2.0,<11.0',
        'moviepy==2.1.2',
        'edge-tts==7.0.0',
        'tqdm>=4.65.0',  # Instead of progress
        'questionary',
        'fsspec[http]<=2024.12.0,>=2023.1.0',
        'numpy<2.2,>=1.24',
        'datasets>=3.5.0',
    ],
    keywords=['python', 'video', 'content creation', 'AI', 'automation', 'editing', 'voiceover synthesis', 'video captions', 'asset sourcing', 'tinyDB'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
