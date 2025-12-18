#!/usr/bin/env python3
import unittest
import networkx as nx

from src.pathfinder import (
    haversine,
    nearest_node,
    djikstra
)

class TestPathfinder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.G = nx.Graph()
        
        # Create a simple grid graph for testing
        # 4 nodes in a square
        cls.node1 = (41.70, -86.24)
        cls.node2 = (41.70, -86.23)
        cls.node3 = (41.69, -86.24)
        cls.node4 = (41.69, -86.23)
        
        # Add edges with weights
        cls.G.add_edge(cls.node1, cls.node2, weight=100)
        cls.G.add_edge(cls.node2, cls.node4, weight=100)
        cls.G.add_edge(cls.node1, cls.node3, weight=100)
        cls.G.add_edge(cls.node3, cls.node4, weight=100)
        cls.G.add_edge(cls.node1, cls.node4, weight=200)  # diagonal
    
    def test_haversine(self):
        # Test same point
        point = (41.70, -86.24)
        self.assertEqual(haversine(point, point), 0.0)
    
    def test_nearest_node(self):
        # Point very close to node1
        test_point = (41.7001, -86.2401)
        nearest = nearest_node(self.G, test_point)
        self.assertEqual(nearest, self.node1)
        
        # Point very close to node4
        test_point = (41.6901, -86.2301)
        nearest = nearest_node(self.G, test_point)
        self.assertEqual(nearest, self.node4)
    
    def test_djikstra_simple_path(self):
        length, path = djikstra(self.G, self.node1, self.node4)
        
        # Should find a path
        self.assertGreater(len(path), 0)
        
        # First node should be end, last should be start
        self.assertEqual(path[0], self.node4)
        self.assertEqual(path[-1], self.node1)
        
        # Length should be positive
        self.assertGreater(length, 0)
    
    def test_djikstra_same_node(self):
        length, path = djikstra(self.G, self.node1, self.node1)
        
        self.assertEqual(length, 0)
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], self.node1)
    
    def test_djikstra_path_symmetry(self):
        length_forward, _ = djikstra(self.G, self.node1, self.node4)
        length_backward, _ = djikstra(self.G, self.node4, self.node1)
        
        self.assertEqual(length_forward, length_backward)
    
    def test_djikstra_optimal_path(self):
        length, path = djikstra(self.G, self.node1, self.node4)
        
        # Direct diagonal edge has weight 200
        # Path via node2 or node3 has weight 200 total (100+100)
        # So optimal path should have length 200
        self.assertEqual(length, 200)

if __name__ == "__main__":
    unittest.main()