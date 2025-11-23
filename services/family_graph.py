"""
Family Graph and Relationship Builder
Creates family trees and calculates relationship distances
"""
import logging
from typing import Dict, List, Optional, Tuple
import networkx as nx
from datetime import datetime

logger = logging.getLogger(__name__)


class FamilyGraphBuilder:
    """
    Build and analyze family relationship graphs
    """

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_person(self, person_id: int, person_data: Dict):
        """
        Add person to family graph

        Args:
            person_id: Person ID
            person_data: Person information
        """
        self.graph.add_node(person_id, **person_data)

    def add_relationship(self, person1_id: int, person2_id: int, relationship_type: str, confidence: float = 1.0):
        """
        Add relationship between two people

        Args:
            person1_id: First person ID
            person2_id: Second person ID
            relationship_type: Type of relationship (parent, child, spouse, sibling)
            confidence: Confidence score (0-1)
        """
        self.graph.add_edge(person1_id, person2_id, relationship=relationship_type, confidence=confidence)

    def calculate_relationship_distance(self, person1_id: int, person2_id: int) -> Optional[int]:
        """
        Calculate degree of separation between two people

        Args:
            person1_id: First person ID
            person2_id: Second person ID

        Returns:
            int: Degrees of separation (None if not connected)
        """
        try:
            # Use shortest path to calculate distance
            path = nx.shortest_path(self.graph.to_undirected(), person1_id, person2_id)
            return len(path) - 1  # Distance is path length minus 1
        except nx.NetworkXNoPath:
            return None

    def get_descendants(self, person_id: int, generations: int = 10) -> List[int]:
        """
        Get all descendants of a person

        Args:
            person_id: Person ID
            generations: Maximum generations to traverse

        Returns:
            list: List of descendant person IDs
        """
        descendants = []

        # BFS to find all descendants
        current_generation = [person_id]
        for gen in range(generations):
            next_generation = []

            for pid in current_generation:
                # Find children (edges where relationship is 'parent')
                for successor in self.graph.successors(pid):
                    edge_data = self.graph.get_edge_data(pid, successor)
                    if edge_data and edge_data.get('relationship') == 'parent':
                        descendants.append(successor)
                        next_generation.append(successor)

            current_generation = next_generation

            if not current_generation:
                break

        return descendants

    def get_ancestors(self, person_id: int, generations: int = 10) -> List[int]:
        """
        Get all ancestors of a person

        Args:
            person_id: Person ID
            generations: Maximum generations to traverse

        Returns:
            list: List of ancestor person IDs
        """
        ancestors = []

        current_generation = [person_id]
        for gen in range(generations):
            next_generation = []

            for pid in current_generation:
                # Find parents (edges where relationship is 'child')
                for predecessor in self.graph.predecessors(pid):
                    edge_data = self.graph.get_edge_data(predecessor, pid)
                    if edge_data and edge_data.get('relationship') == 'parent':
                        ancestors.append(predecessor)
                        next_generation.append(predecessor)

            current_generation = next_generation

            if not current_generation:
                break

        return ancestors

    def get_siblings(self, person_id: int) -> List[int]:
        """
        Get siblings of a person

        Args:
            person_id: Person ID

        Returns:
            list: List of sibling person IDs
        """
        siblings = []

        # Get parents
        parents = []
        for predecessor in self.graph.predecessors(person_id):
            edge_data = self.graph.get_edge_data(predecessor, person_id)
            if edge_data and edge_data.get('relationship') == 'parent':
                parents.append(predecessor)

        # Get other children of parents
        for parent in parents:
            for child in self.graph.successors(parent):
                edge_data = self.graph.get_edge_data(parent, child)
                if edge_data and edge_data.get('relationship') == 'parent' and child != person_id:
                    if child not in siblings:
                        siblings.append(child)

        return siblings

    def identify_heirs(self, deceased_id: int) -> List[Tuple[int, int, float]]:
        """
        Identify legal heirs of deceased person

        Args:
            deceased_id: ID of deceased person

        Returns:
            list: List of (person_id, degree, probability) tuples
        """
        heirs = []

        # Priority 1: Direct children
        children = []
        for successor in self.graph.successors(deceased_id):
            edge_data = self.graph.get_edge_data(deceased_id, successor)
            if edge_data and edge_data.get('relationship') == 'parent':
                children.append(successor)

        if children:
            # Children inherit - degree 1
            for child in children:
                confidence = edge_data.get('confidence', 1.0)
                heirs.append((child, 1, 1.0 * confidence))
            return heirs

        # Priority 2: Spouse (if no children)
        # Note: Spouse relationship would need to be modeled separately

        # Priority 3: Grandchildren (if no children)
        grandchildren = []
        for child in children:  # This would be empty if we got here, but shows the pattern
            for grandchild in self.get_descendants(child, 1):
                grandchildren.append(grandchild)

        if grandchildren:
            for gc in grandchildren:
                heirs.append((gc, 2, 0.85))
            return heirs

        # Priority 4: Siblings
        siblings = self.get_siblings(deceased_id)
        if siblings:
            for sibling in siblings:
                heirs.append((sibling, 2, 0.75))
            return heirs

        # Priority 5: Nieces/nephews
        nieces_nephews = []
        for sibling in siblings:
            for child in self.get_descendants(sibling, 1):
                nieces_nephews.append(child)

        if nieces_nephews:
            for nn in nieces_nephews:
                heirs.append((nn, 3, 0.65))
            return heirs

        return heirs

    def export_to_dict(self) -> Dict:
        """
        Export graph to dictionary format

        Returns:
            dict: Graph data
        """
        return {
            'nodes': [
                {'id': node, **data}
                for node, data in self.graph.nodes(data=True)
            ],
            'edges': [
                {
                    'from': u,
                    'to': v,
                    'relationship': data.get('relationship'),
                    'confidence': data.get('confidence', 1.0)
                }
                for u, v, data in self.graph.edges(data=True)
            ]
        }

    def export_to_cytoscape(self) -> Dict:
        """
        Export graph in Cytoscape.js format for visualization

        Returns:
            dict: Cytoscape-compatible data
        """
        elements = []

        # Nodes
        for node, data in self.graph.nodes(data=True):
            elements.append({
                'data': {
                    'id': str(node),
                    'label': data.get('name', f'Person {node}'),
                    **data
                }
            })

        # Edges
        for u, v, data in self.graph.edges(data=True):
            elements.append({
                'data': {
                    'source': str(u),
                    'target': str(v),
                    'label': data.get('relationship', ''),
                    **data
                }
            })

        return {'elements': elements}

    @staticmethod
    def from_database(property_id: Optional[int] = None) -> 'FamilyGraphBuilder':
        """
        Build family graph from database

        Args:
            property_id: Optional property ID to build graph for specific case

        Returns:
            FamilyGraphBuilder: Populated graph
        """
        from models import Person, person_relationships, db

        graph_builder = FamilyGraphBuilder()

        # Get all people (or filtered by property)
        if property_id:
            # Get heirs for this property
            from models import Heir
            heirs = Heir.query.filter_by(property_id=property_id).all()

            # Get associated persons
            person_ids = [h.person_id for h in heirs if h.person_id]
            people = Person.query.filter(Person.id.in_(person_ids)).all() if person_ids else []
        else:
            people = Person.query.all()

        # Add people as nodes
        for person in people:
            graph_builder.add_person(person.id, {
                'name': person.full_name(),
                'birth_date': person.date_of_birth,
                'death_date': person.date_of_death,
                'confidence': person.confidence_score
            })

        # Add relationships from person_relationships table
        relationships = db.session.query(person_relationships).all()

        for rel in relationships:
            graph_builder.add_relationship(
                rel.person_id,
                rel.related_person_id,
                rel.relationship_type,
                rel.confidence_score or 1.0
            )

        return graph_builder
