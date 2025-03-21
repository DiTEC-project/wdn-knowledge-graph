from setuptools import setup, find_packages

setup(
    name="wdn-knowledge-graph",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        'networkx',
        'wntr',
        'rdflib',
    ],
    package_data={
        'wdn_knowledge_graph': ['wdn_ontology.ttl'],
    },
    entry_points={
        'console_scripts': [
            'create-knowledge-graph=wdn_knowledge_graph.knowledge_graph:main',
        ],
    },
    author="Erkan Karabulut",
    author_email="e.karabulut@uva.nl",
    description="A package for creating knowledge graphs from water distribution network data.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DiTEC-project/wdn-knowledge-graph",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
