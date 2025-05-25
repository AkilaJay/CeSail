from typing import List, Dict, Any
from .types import ElementInfo, Action, ActionGraph

class SensitiveHandler:
    def __init__(self):
        self.sensitive_patterns = {
            'password': ['password', 'passwd', 'pwd', 'secret'],
            'email': ['email', 'mail', 'username', 'user'],
            'credit_card': ['card', 'credit', 'ccv', 'cvv', 'expiry'],
            'phone': ['phone', 'mobile', 'tel', 'cell'],
            'ssn': ['ssn', 'social', 'security'],
        }

    def process_action_graph(self, action_graph: ActionGraph) -> ActionGraph:
        """Process the action graph to identify and handle sensitive elements."""
        # Deep copy the action graph to avoid modifying the original
        processed_graph = action_graph.copy()
        
        # Process each node
        for node in processed_graph.nodes:
            self._process_element(node)
        
        # Process each action
        for action in processed_graph.edges:
            self._process_action(action)
        
        return processed_graph

    def _process_element(self, element: ElementInfo):
        """Process a single element to identify sensitive information."""
        # Check element attributes for sensitive patterns
        for attr_name, attr_value in element.attributes.items():
            if self._is_sensitive_attribute(attr_name, attr_value):
                element.is_sensitive = True
                break

        # Check element text for sensitive patterns
        if element.text and self._is_sensitive_text(element.text):
            element.is_sensitive = True

        # Process children recursively
        for child in element.children:
            self._process_element(child)

    def _process_action(self, action: Action):
        """Process a single action to handle sensitive information."""
        if action.type == 'input':
            # Check if the action is related to a sensitive field
            if any(pattern in action.description.lower() for patterns in self.sensitive_patterns.values() for pattern in patterns):
                action.metadata['is_sensitive'] = True
                action.description = "Enter sensitive information"

    def _is_sensitive_attribute(self, attr_name: str, attr_value: str) -> bool:
        """Check if an attribute name or value contains sensitive patterns."""
        attr_lower = f"{attr_name} {attr_value}".lower()
        return any(
            pattern in attr_lower
            for patterns in self.sensitive_patterns.values()
            for pattern in patterns
        )

    def _is_sensitive_text(self, text: str) -> bool:
        """Check if text contains sensitive patterns."""
        text_lower = text.lower()
        return any(
            pattern in text_lower
            for patterns in self.sensitive_patterns.values()
            for pattern in patterns
        )
