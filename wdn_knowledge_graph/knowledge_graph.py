import argparse
import enum

import networkx as nx
import wntr
import pkg_resources
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD
import sys


def create_knowledge_graph_from_inp(inp_file, destination="knowledge_graph.ttl"):
    # Extract namespace from the ontology TTL file
    wdn_namespace = Namespace(
        'https://raw.githubusercontent.com/DiTEC-project/wdn-knowledge-graph/refs/heads/main/wdn_ontology.ttl')
    if not wdn_namespace:
        print("Error: Could not extract the 'wdn' namespace from the ontology file.")
        sys.exit(1)

    # Load the network using WNTR
    wn = wntr.network.WaterNetworkModel(inp_file)

    # Create an RDF graph to store the knowledge graph
    g = Graph()

    # Bind the prefix for the ontology using the extracted namespace
    g.bind('wdn', wdn_namespace)
    g.bind('rdf', RDF)
    g.bind('rdfs', RDFS)
    g.bind('xsd', XSD)

    # Process Junctions
    for junction_name, junction_obj in wn.junctions():
        junction_uri = URIRef(wdn_namespace[f"Junction_{junction_name}"])
        g.add((junction_uri, RDF.type, wdn_namespace.Junction))
        g.add((junction_uri, RDFS.label, Literal(f"Junction {junction_name}")))

        # Elevation
        g.add((junction_uri, wdn_namespace.elevation, Literal(junction_obj.elevation, datatype=XSD.double)))

        # Demand
        if junction_obj.demand_timeseries_list:
            demand_obj = junction_obj.demand_timeseries_list[0]  # Assuming one demand series
            if demand_obj.base_value is not None:
                g.add((junction_uri, wdn_namespace.baseDemand, Literal(demand_obj.base_value, datatype=XSD.double)))

    # Process Reservoirs
    for reservoir_name, reservoir_obj in wn.reservoirs():
        reservoir_uri = URIRef(wdn_namespace[f"Reservoir_{reservoir_name}"])
        g.add((reservoir_uri, RDF.type, wdn_namespace.Reservoir))
        g.add((reservoir_uri, RDFS.label, Literal(f"Reservoir {reservoir_name}")))

        # Head
        g.add((reservoir_uri, wdn_namespace.head, Literal(reservoir_obj.base_head, datatype=XSD.double)))

    # Process Tanks
    for tank_name, tank_obj in wn.tanks():
        tank_uri = URIRef(wdn_namespace[f"Tank_{tank_name}"])
        g.add((tank_uri, RDF.type, wdn_namespace.Tank))
        g.add((tank_uri, RDFS.label, Literal(f"Tank {tank_name}")))

        # Elevation, Initial Level, Min/Max Levels
        g.add((tank_uri, wdn_namespace.bottomElevation, Literal(tank_obj.elevation, datatype=XSD.double)))
        g.add((tank_uri, wdn_namespace.initialLevel, Literal(tank_obj.init_level, datatype=XSD.double)))
        g.add((tank_uri, wdn_namespace.minLevel, Literal(tank_obj.min_level, datatype=XSD.double)))
        g.add((tank_uri, wdn_namespace.maxLevel, Literal(tank_obj.max_level, datatype=XSD.double)))
        g.add((tank_uri, wdn_namespace.diameter, Literal(tank_obj.diameter, datatype=XSD.double)))

    # Process Pipes
    for pipe_name, pipe_obj in wn.pipes():
        pipe_uri = URIRef(wdn_namespace[f"Pipe_{pipe_name}"])
        g.add((pipe_uri, RDF.type, wdn_namespace.Pipe))
        g.add((pipe_uri, RDFS.label, Literal(f"Pipe {pipe_name}")))

        # Length, Diameter, Roughness, Status
        g.add((pipe_uri, wdn_namespace.length, Literal(pipe_obj.length, datatype=XSD.double)))
        g.add((pipe_uri, wdn_namespace.diameter, Literal(pipe_obj.diameter, datatype=XSD.double)))
        g.add((pipe_uri, wdn_namespace.roughness, Literal(pipe_obj.roughness, datatype=XSD.double)))
        g.add((pipe_uri, wdn_namespace.status, Literal(pipe_obj.status, datatype=XSD.string)))

        # Object Properties: hasStartNode and hasEndNode
        start_node_uri = URIRef(wdn_namespace[f"{pipe_obj.start_node.node_type}_{pipe_obj.start_node_name}"])
        end_node_uri = URIRef(wdn_namespace[f"{pipe_obj.end_node.node_type}_{pipe_obj.end_node_name}"])

        g.add((pipe_uri, wdn_namespace.hasStartNode, start_node_uri))
        g.add((pipe_uri, wdn_namespace.hasEndNode, end_node_uri))

    # Process Pumps
    for pump_name, pump_obj in wn.pumps():
        pump_uri = URIRef(wdn_namespace[f"Pump_{pump_name}"])
        g.add((pump_uri, RDF.type, wdn_namespace.Pump))
        g.add((pump_uri, RDFS.label, Literal(f"Pump {pump_name}")))

        # Object Property: Pumps Water to Tanks
        node_uri = URIRef(wdn_namespace[f"{pump_obj.start_node.node_type}_{pump_obj.start_node_name}"])
        tank_uri = URIRef(wdn_namespace[f"{pump_obj.start_node.node_type}_{pump_obj.end_node_name}"])
        g.add((pump_uri, wdn_namespace.pumpsReceiveWaterFrom, node_uri))
        g.add((pump_uri, wdn_namespace.pumpsWaterTo, tank_uri))

    # Process Valves
    for valve_name, valve_obj in wn.valves():
        valve_uri = URIRef(wdn_namespace[f"Valve_{valve_name}"])
        g.add((valve_uri, RDF.type, wdn_namespace.Valve))
        g.add((valve_uri, RDFS.label, Literal(f"Valve {valve_name}")))

        # Setting
        g.add((valve_uri, wdn_namespace.setting, Literal(valve_obj.setting)))

        # Object Property: Regulates Flow in Pipes
        start_node_uri = URIRef(wdn_namespace[f"Node_{valve_obj.start_node_name}"])
        end_node_uri = URIRef(wdn_namespace[f"Node_{valve_obj.end_node_name}"])

        g.add((valve_uri, wdn_namespace.hasStartNode, start_node_uri))
        g.add((valve_uri, wdn_namespace.hasEndNode, end_node_uri))

    # Serialize the graph to a .ttl file
    g.serialize(destination=destination, format='turtle')
    print(f"A knowledge graph has been created and saved to {destination}")
    return g


def networkx(rdf_graph):
    """
    Convert an RDFLib graph to a NetworkX graph.
    - Nodes: All individuals and ontology classes.
    - Edges: Object properties create directed edges between nodes.
    - Attributes: Data properties are stored as node attributes.
    """
    if isinstance(rdf_graph, Graph) or isinstance(rdf_graph, str):
        if isinstance(rdf_graph, Graph):
            rdf_graph = rdf_graph
        elif isinstance(rdf_graph, str):
            if rdf_graph.endswith('.ttl'):
                try:
                    rdf_graph = Graph().parse(rdf_graph, format='turtle')
                except Exception as e:
                    print(f"Error parsing Turtle file: {e}")
                    return None
            else:
                print("Unexpected input format. Provide a Turtle (.ttl) file path.")
    else:
        print("Unexpected input format. Provide an RDFLib Graph or a .ttl file path.")
        return None

    # Initialize the directed graph
    nx_graph = nx.DiGraph()

    # Process the RDF graph
    for s, p, o in rdf_graph:
        s, p = s.toPython(), p.toPython()
        # Ensure subject is a node
        if s not in nx_graph:
            nx_graph.add_node(s)

        # Check if the object is a literal (data property) or an entity (object property)
        if isinstance(o, Literal):  # Data property → store as a node attribute
            nx_graph.nodes[s][p] = o.toPython()
        else:  # Object property → add an edge
            o = o.toPython()
            # in case o is not a hashable type, parse it to string
            if isinstance(o, enum.Enum):
                o = str(o)
            nx_graph.add_edge(s, o, predicate=p)

    return nx_graph


def get_default_ontology_file():
    # Use pkg_resources to access the ontology file packaged within the distribution
    ontology_file = pkg_resources.resource_filename(
        'wdn_knowledge_graph',  # Name of the package (should match the directory name)
        'wdn_ontology.ttl'  # The file path relative to the package
    )
    return ontology_file


def main():
    parser = argparse.ArgumentParser(description="Convert .inp water network files into RDF knowledge graphs.")
    parser.add_argument("-i", "--inp-file", help="Path to the .inp file")
    parser.add_argument("-d", "--destination", help="Path to the file to save the knowledge graph into.",
                        default="knowledge_graph.ttl")

    args = parser.parse_args()
    ontology_file = get_default_ontology_file()
    print(f"Using the ontology file {ontology_file} for populating the knowledge graph.")
    create_knowledge_graph_from_inp(args.inp_file, args.destination)

    # ontology = Graph().parse(ontology_file, format="ttl")
    # networkx_format = networkx(kg)


if __name__ == "__main__":
    main()
