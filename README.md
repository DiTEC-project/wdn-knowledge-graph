# wdn-knowledge-graph

`wdn-knowledge-graph` is a Python package designed to convert water distribution network (WDN) data from `.inp` files
(the standard format for the [EPANET](https://epanet22.readthedocs.io/en/latest/3_network_model.html) tool) into **RDF
knowledge graphs** in the `.ttl` format using a WDN ontology we created.

The **WDN ontology**
in [`wdn_ontology.ttl`](https://github.com/DiTEC-project/wdn-knowledge-graph/blob/main/wdn_ontology.ttl) captures the
physical components of a WDN, inspired from the EPANET tool.

This package also provides the possibility of converting the final knowledge graph to the
popular [NetworkX](https://networkx.org/) format for further processing, making it easier to analyze and
manipulate the water distribution network data.

---

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
    - [Command-Line Interface (CLI)](#command-line-interface--cli-)
    - [Using in a Python Program](#using-in-a-python-program)
- [About](#about)
- [Functions](#functions)
    - [Create knowledge grap from .inp](#create-knowledge-grap-from-inp)
    - [Convert knowledge graph to NetworkX](#convert-knowledge-graph-to-networkx)
- [Citation](#citation)
- [Contact](#contact)
- [Contributing](#contributing)

---

## Introduction

`wdn-knowledge-graph` is a tool for creating RDF-based knowledge graphs from water distribution network (WDN) data. It
reads an `.inp` file (the standard format for EPANET) and an ontology `.ttl` file, then generates a knowledge graph
representing the water network. The package also provides a method to convert the generated RDF graph into a NetworkX
graph for further analysis, leveraging the power of the NetworkX Python package.

You can use this package to model and analyze water distribution networks with ease and flexibility.

Please remember to [**cite**](#citation) our paper if you use this package in your work:

## Installation

You can install `wdn-knowledge-graph` via pip:

```bash
pip install wdn-knowledge-graph
```

## Usage

### Command-Line Interface (CLI)

Once the package is installed, you can use it directly from the command line to construct a knowledge graph from a water
distribution network .inp file. The construction of the knowledge graph uses our Water Distribution Network
ontology ([wdn_ontology.ttl](https://github.com/DiTEC-project/wdn-knowledge-graph/blob/main/wdn_ontology.ttl)).

```bash
create-knowledge-graph -i path_to_input_file.inp -d knowledge_graph.ttl
```

-i : Path to the .inp file containing water network data.

-d : Path to the output .ttl file to save the generated knowledge graph.

### Using in a Python Program

Alternatively, you can use the package directly within a Python program by importing its functions. This allows for more
flexibility in how you integrate it into your project.

**Example**:

```
from rdflib import Graph
from wdn_knowledge_graph.knowledge_graph import create_knowledge_graph_from_inp, networkx

# Define file paths
inp_file = 'EPANET input file.inp'
output_file = 'knowledge_graph.ttl'
ontology_file = 'wdn_ontology.ttl'

# Create the knowledge graph
knowledge_graph = create_knowledge_graph_from_inp(inp_file, destination=output_file)

# Convert the RDF knowledge graph to a NetworkX graph for further processing
networkx_graph = networkx(knowledge_graph)

print(networkx_graph)

```

In this example:

- `create_knowledge_graph_from_inp()` is used to generate the RDF knowledge graph from the .inp file and ontology.
- `networkx()` is then used to convert the RDF graph into a NetworkX graph, which can be analyzed or manipulated
  further.

## About

This section explains some of the fundamental concepts behind the .inp file, .ttl (Turtle) files, EPANET, ontologies,
and knowledge graphs that are used in this package.

- **[EPANET](https://epanet22.readthedocs.io/en/latest/3_network_model.html)** is a software application used to
  simulate water distribution systems. It models the hydraulic and water
  quality behavior of water distribution networks. EPANET uses the .inp file format to store input data describing the
  network, including pipes, junctions, tanks, reservoirs, and pumps.

- **Turtle** (TTL) is a human-readable serialization format for RDF (Resource Description Framework) data. RDF is a
  standard model for data interchange on the web. In the context of this package, TTL files are used to store knowledge
  graphs, which represent relationships between different entities (e.g., junctions, pipes, tanks).

- The **.inp file** format is a text-based format used by EPANET to define the components of a water distribution
  system, including junctions, pipes, pumps, valves, tanks, and reservoirs. These files contain data such as pipe
  lengths, junction demands, tank levels, etc., that describe how the water distribution system operates.
  Ontology and Knowledge Graph

- An **ontology** is a formal representation of knowledge within a particular domain. It defines the concepts, entities,
  and relationships that exist within that domain.

- A **knowledge graph** is a graph-based representation of information where nodes represent entities, and edges
  represent the relationships between these entities. It is often used to represent complex data, and in this case, the
  package creates a knowledge graph of a water distribution network.

Additionally, we provide a water distribution network ontology in the [wdn_ontology.ttl](wdn_ontology.ttl) file in the
main folder. This ontology defines the relevant classes, properties, and relationships specific to water distribution
networks.

### Key Python Packages Used

This package makes use of several popular Python libraries for ease of use and performance:

- [WNTR](https://github.com/USEPA/WNTR): A Python package for modeling and analyzing water distribution networks.
- [RDFLib](https://rdflib.readthedocs.io/en/stable/): A Python library for working with RDF data, parsing and
  serializing RDF files, and querying them using SPARQL.
- [NetworkX](https://networkx.org/): A Python package for the creation, manipulation, and study of the structure,
  dynamics, and functions of complex networks.

### Sample Data

The sample data folder includes knowledge graphs created for the [L-Town](https://zenodo.org/records/4017659)
and [LeakDB](https://github.com/KIOS-Research/LeakDB) (Scenario 1) datasets.

- [Knowledge graph](https://github.com/DiTEC-project/wdn-knowledge-graph/blob/main/sample_data/L-TOWN%20-%20Knowledge%20Graph.ttl)
  constructed from the L-Town dataset
- [Knowledge graph](https://github.com/DiTEC-project/wdn-knowledge-graph/blob/main/sample_data/LeakDB%20Scenario%201%20-%20Knowledge%20Graph.ttl)
  constructed from the LeakDB dataset

## Functions

### Create knowledge grap from .inp

**create_knowledge_graph_from_inp(inp_file, ontology_file, destination="output.ttl")**

This function generates a knowledge graph in Turtle format (.ttl) from a water network .inp file and an ontology .ttl
file. It creates an RDF graph representing the various entities in the water distribution system (e.g., junctions,
pipes, tanks, etc.).

**Parameters**:

- inp_file: The path to the .inp file containing water network data.
- ontology_file: The path to the ontology .ttl file.
- destination: The file path to save the generated RDF graph (default is output.ttl).

**Returns**:

- An RDF Graph object representing the knowledge graph.

### Convert knowledge graph to NetworkX

**networkx(rdf_graph)**

This function converts a Turtle file (knowledge graph) to a NetworkX graph for easier analysis and manipulation.
It accepts either in RDFlib graph format or a string path to where the .ttl file is located. It processes both object
properties and data properties from the ontology to create the appropriate nodes and edges in the NetworkX graph.

**Parameters**:

- rdf_graph: An RDFlib Graph object or a .ttl file with the knowledge graph to be converted.

**Returns**:

- A NetworkX directed graph (DiGraph).

## Citation

If you use this package in your research or work, please cite the following paper:

    @article{karabulut2024learning,
      title={Learning Semantic Association Rules from Internet of Things Data},
      author={Karabulut, Erkan and Groth, Paul and Degeler, Victoria},
      journal={arXiv preprint arXiv:2412.03417},
      year={2024}
    }

## Contact

If you have any questions or improvement ideas, feel free to contact Erkan Karabulut at:

**Email**: e.karabulut@uva.nl

## Contributing

You can contribute to the project in any way you see fit! Whether it’s updating our WDN ontology, reporting bugs,
suggesting new features, or submitting code, your input is welcome.

To contribute, please visit the project’s GitHub repository and start a discussion:

**GitHub**: [wdn-knowledge-graph](https://github.com/DiTEC-project/wdn-knowledge-graph)