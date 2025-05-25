import asyncio
from dom_parser.src.graph_generator import GraphGenerator

async def main():
    # Example URL to analyze
    url = "https://example.com"
    
    # Using the context manager (recommended)
    async with GraphGenerator(headless=True) as generator:
        # Generate the action graph
        action_graph = await generator.generate_graph(url)
        
        # Print some basic information
        print(f"Analyzed URL: {action_graph.url}")
        print(f"Number of elements found: {len(action_graph.nodes)}")
        print(f"Number of possible actions: {len(action_graph.edges)}")
        
        # Print all possible actions
        print("\nPossible actions:")
        for i, action in enumerate(action_graph.edges, 1):
            print(f"{i}. {action.description} (Confidence: {action.confidence:.2f})")
            if action.metadata.get('is_sensitive'):
                print("   [Sensitive field]")

if __name__ == "__main__":
    asyncio.run(main()) 