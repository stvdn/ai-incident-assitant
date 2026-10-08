import os


def required_env(name: str) -> str:
    value = os.environ.get(name)

    if value is None or not value.strip():
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value

def postgres_port() -> int:
    message = "POSTGRES_PORT must be an integer between 1 and 65535"

    try:
        port = int(required_env("POSTGRES_PORT"))
    except ValueError:
        raise RuntimeError(message) from None

    if not 1 <= port <= 65535:
        raise RuntimeError(message)

    return port
