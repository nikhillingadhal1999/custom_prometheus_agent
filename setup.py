from setuptools import setup, find_packages

setup(
    name="flexmetric",
    version="0.1.0",
    author="Nikhil Lingadhal",
    description="A flexible Prometheus exporter for commands, databases, functions, and scripts.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/nikhillingadhal1999/custom_prometheus_agent",
    license="MIT",
    packages=find_packages(),  # Auto-detects submodules in flexmetric/
    install_requires=[
        "prometheus_client",
        "PyYAML",
        "psutil",
        "setuptools",
        "wheel",
        "twine"
    ],
    entry_points={
        "console_scripts": [
            "flexmetric = flexmetric.metric_process.prometheus_agent:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
