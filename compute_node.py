from lib import compute_node

if __name__ == "__main__":
    try:
        compute_node.run_websocket_server(verbose=True)
    except KeyboardInterrupt:
        print("\nShutting down compute node gracefully...")
    except Exception as e:
        print(f"\nError in compute node: {e}")
