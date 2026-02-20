"""A debug proxy entryance point."""

import sys

from gradient_server.server import serve_from_cli

if __name__ == "__main__":
    argv = sys.argv[1:]

    serve_from_cli(argv)
