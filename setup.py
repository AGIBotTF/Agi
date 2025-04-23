from setuptools import setup, find_packages

setup(
    name="assistant",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "openai",
        "gTTS",
        "pydub",
        "SpeechRecognition",
        "pyaudio",
        "numpy",
        "scipy",
        "python-dotenv"
    ],
    python_requires=">=3.8",
) 