import unittest
import os
from rdflib import Graph
from wdn_knowledge_graph.knowledge_graph import create_knowledge_graph_from_inp


class TestKnowledgeGraphCreator(unittest.TestCase):

    def test_create_knowledge_graph_from_inp(self):
        # This is a mock test to check if the knowledge graph is created
        inp_file = "../sample_data/LeakDB_Scenario-1.inp"
        ontology_file = "wdn_ontology.ttl"
        expected_ttl_file = "../sample_data/LeakDB Scenario 1 - Knowledge Graph.ttl"  # Path to the expected .ttl file
        generated_ttl_file = "generated_ttl_file.ttl"

        try:
            # Create the knowledge graph
            result = create_knowledge_graph_from_inp(inp_file, ontology_file, destination=generated_ttl_file)

            # Load the expected RDF graph from the file
            expected_graph = Graph()
            expected_graph.parse(expected_ttl_file, format="ttl")

            # Load the generated RDF graph for comparison
            generated_graph = Graph()
            generated_graph.parse(generated_ttl_file, format="ttl")

            # Compare the graphs: the generated graph should match the expected graph
            self.assertEqual(len(expected_graph), len(generated_graph), "Graphs have different sizes.")

            # Check that the content of both graphs is identical
            for triple in expected_graph:
                self.assertIn(triple, generated_graph, f"Triple {triple} not found in the generated graph.")

        finally:
            # Clean up the generated graph file after the test, even if assertions fail
            if os.path.exists(generated_ttl_file):
                os.remove(generated_ttl_file)


if __name__ == '__main__':
    unittest.main()
