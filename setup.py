from setuptools import setup, find_packages

setup(
    name="MusicChecker",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "librosa",
        "numpy",
        "tkinter",  # included with Python on Windows/Mac, may need manual install on Linux
    ],
    entry_points={
        "console_scripts": [
            "musicchecker-cli=music_checker_cli.music_checker_cli:scan_music_folder",
        ],
    },
    author='Brad "twistedp469" Crow',
    description="Tool for detecting and quarantining silent or whisper-level audio files (GUI + CLI).",
    license="MIT",
    url="https://github.com/twistedp469/MusicChecker",
)
