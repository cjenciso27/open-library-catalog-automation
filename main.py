from src.config import get_settings


def main() -> None:
    settings = get_settings()
    print(f"Open Library Intelligence & Catalog Automation System - API: {settings.api_base_url}")


if __name__ == "__main__":
    main()
