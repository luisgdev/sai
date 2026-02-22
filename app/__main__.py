"""Main module."""

from app.session import ChatSession


def main() -> None:
    """Main entry point."""
    session = ChatSession()
    session.run()


if __name__ == "__main__":
    main()
