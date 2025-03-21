import argparse

import networkx as nx
import wntr
from rdflib import Graph, URIRef, Literal, Namespace, OWL
from rdflib.namespace import RDF, RDFS, XSD
import sys


def extract_namespace_from_ontology(ontology_file):
    # Parse the ontology file to extract the namespace
    g = Graph()
    g.parse(ontology_file, format='turtle')

    # Extract the namespace URI from the prefixes
    for prefix, namespace in g.namespaces():
        if prefix == 'wdn':  # Assuming 'wdn' is the prefix for our ontology
            return Namespace(namespace)
    return None  # Return None if 'wdn' prefix is not found


def create_knowledge_graph_from_inp(inp_file, ontology_file, destination="LeakDB Scenario 1 - Knowledge Graph.ttl"):
    # Extract namespace from the ontology TTL file
    wdn_namespace = extract_namespace_from_ontology(ontology_file)
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
        end_node_uri = URIRef(wdn_namespace[f"{pipe_obj.start_node.node_type}_{pipe_obj.end_node_name}"])

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


def networkx(rdf_graph: Graph, ontology: Graph):
    """
    Convert an RDFLib graph to a NetworkX graph.

    - Nodes: All individuals and ontology classes.
    - Edges: Object properties create directed edges between nodes.
    - Attributes: Data properties are stored as node attributes.
    """
    # Initialize the directed graph
    nx_graph = nx.DiGraph()

    # First, we collect all object properties and data properties from the ontology
    object_properties = set()
    datatype_properties = set()

    # Iterate over the ontology graph to find object and datatype properties
    for s, p, o in ontology:
        # Check if the predicate (p) is rdf:type and the object (o) is OWL.ObjectProperty
        if p == RDF.type and o == OWL.ObjectProperty:
            object_properties.add(str(s))  # Add ObjectProperty to the set
        # Check if the predicate (p) is rdf:type and the object (o) is OWL.DatatypeProperty
        elif p == RDF.type and o == OWL.DatatypeProperty:
            datatype_properties.add(str(s))  # Add DatatypeProperty to the set

    # Now process the RDF graph
    for s, p, o in rdf_graph:
        s_str, p_str, o_str = str(s), str(p), str(o)

        # Add nodes (subjects and objects) to the graph
        if (s, RDF.type, None) in rdf_graph:  # If subject is a known entity
            nx_graph.add_node(s_str)
        if (o, RDF.type, None) in rdf_graph:  # If object is a known entity
            nx_graph.add_node(o_str)

        # Check if the predicate is a data property or object property using the ontology
        if p_str in datatype_properties:
            # Data property → add as node attribute
            nx_graph.nodes[s_str][p_str] = o_str
        elif p_str in object_properties:
            # Object property → add as an edge
            nx_graph.add_edge(s_str, o_str, predicate=p_str)

    return nx_graph


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert .inp water network files into RDF knowledge graphs.")
    parser.add_argument("-i", "--inp-file", help="Path to the .inp file")
    parser.add_argument("-o", "--ontology-file", nargs="?", default="wdn_ontology.ttl",
                        help="Path to the ontology file (default: wdn_ontology.ttl)")
    parser.add_argument("-d", "--destination", help="Path to the file to save the knowledge graph into.",
                        default="knowledge_graph.ttl")

    args = parser.parse_args()

    print(f"Using the ontology file {args.ontology_file} for populating the knowledge graph.")
    knowledge_graph = create_knowledge_graph_from_inp(args.inp_file, args.ontology_file, args.destination)

    ontology = Graph().parse(args.ontology_file, format="ttl")
    networkx_format = networkx(knowledge_graph, ontology)
