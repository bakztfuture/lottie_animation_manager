import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lottie-animation-manager", # Replace with your own username
    version="0.0.5",
    author="Bakz T. Future",
    author_email="bakztfuture@gmail.com",
    description="The easiest way to manage, compress, and upload Lottie assets to a CDN.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bakztfuture/lottie_animation_manager",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        "console_scripts": [
            "lottie-animation-manager = lottie_animation_manager.__main__:initialize_configuration",
        ]
    },
    install_requires=[
        'boto>=2.49',
        'click>=7.1',
        'colorama>=0.4',
        'emoji>=0.5',
        'pyfiglet>=0.8',
        'tinify>=1.5'
    ],
    python_requires='>=3.6',
    keywords='lottie animations bodymovin cloudfront cdn',
)