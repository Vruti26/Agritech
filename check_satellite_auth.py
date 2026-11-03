from services.sentinelhub_service import get_access_token


def main():
    try:
        token_data = get_access_token()

        print("Copernicus authentication successful.")
        print(f"Token type: {token_data.get('token_type')}")
        print(f"Expires in: {token_data.get('expires_in')} seconds")
        print("Access token received: Yes")
        print("Access token value: [not displayed]")

    except RuntimeError as exc:
        print(f"Authentication check failed: {exc}")


if __name__ == "__main__":
    main()