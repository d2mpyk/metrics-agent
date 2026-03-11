from setuptools import setup, find_packages

setup(
    name="wise_agent",
    version="1.0.0",
    description="Agente de recolección de métricas de sistema para WISE Management",
    author="WISE Team",
    packages=find_packages(),
    py_modules=["main", "agent"],
    entry_points={
        "console_scripts": [
            "wise-agent=main:main",
        ],
    },
    install_requires=[
        "requests>=2.31.0",
        "psutil>=5.9.0",
        "cryptography>=42.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
