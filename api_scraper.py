import re
import shlex
import json
import uuid


def process_endpoint(original_endpoint: str):
    """
    Process the original endpoint URL.
    - Strips query parameters from the endpoint.
    - Returns (clean_endpoint, query_headers) where:
         clean_endpoint: endpoint without query string.
         query_headers: list of header entries for each query parameter.
    """
    query_headers = []
    if original_endpoint and "?" in original_endpoint:
        base, query = original_endpoint.split("?", 1)
        for param in query.split("&"):
            if "=" in param:
                key, value = param.split("=", 1)
            else:
                key, value = param, ""
            query_headers.append(
                {"key": key, "value": value, "active": True, "description": ""}
            )
        return base, query_headers
    return original_endpoint, query_headers


def derive_request_name(original_endpoint: str, idx: int) -> str:
    """
    Derive a request name from the original endpoint.
    Removes query parameters, then takes the last segment.
    If the last segment is numeric and there's a preceding segment,
    returns "precedingSegment/numeric". Otherwise, returns the last segment.
    If original_endpoint is empty, returns "Request {idx}".
    """
    if not original_endpoint:
        return f"Request {idx}"
    # Remove query parameters
    endpoint_no_query = original_endpoint.split("?", 1)[0]
    segments = endpoint_no_query.rstrip("/").split("/")
    if segments:
        if segments[-1].isdigit() and len(segments) >= 2:
            return f"{segments[-2]}/{segments[-1]}"
        else:
            return segments[-1]
    return f"Request {idx}"


def normalize_authorization(auth_value: str) -> str:
    """
    Normalize the Authorization header value.
    If it starts with 'Token ', replace its token with a placeholder.
    """
    if auth_value.startswith("Token "):
        return "Token <<TOKEN>>"
    return auth_value


def parse_curl(curl_command: str) -> dict:
    """
    Parse a single curl command and return a dictionary with:
      - method: HTTP method.
      - endpoint: URL.
      - headers: list of header dictionaries {name, value}.
      - body: raw data string (empty string if none).
    """
    # Remove backslash-newline continuations and extra spaces.
    command = curl_command.replace("\\\n", " ").strip()
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = shlex.split(command, posix=False)

    url = None
    method = None
    headers = []
    data = None
    i = 1  # skip the "curl" token
    while i < len(tokens):
        token = tokens[i]
        if token.startswith("http"):
            url = token
        elif token in ("-X", "--request"):
            i += 1
            method = tokens[i].upper()
        elif token in ("--data-raw", "--data"):
            i += 1
            data = tokens[i]
            # Remove a leading $ if present.
            if data.startswith("$"):
                data = data[1:]
            # Remove surrounding quotes if present.
            if (data.startswith("'") and data.endswith("'")) or (
                data.startswith('"') and data.endswith('"')
            ):
                data = data[1:-1]
        elif token in ("-H", "--header"):
            i += 1
            header_line = tokens[i]
            if ": " in header_line:
                key, value = header_line.split(": ", 1)
            elif ":" in header_line:
                key, value = header_line.split(":", 1)
            else:
                key, value = header_line, ""
            headers.append({"name": key.strip(), "value": value.strip()})
        i += 1

    if method is None:
        method = "POST" if data is not None else "GET"

    return {
        "method": method,
        "endpoint": url,
        "headers": headers,
        "body": data if data is not None else "",
    }


def generate_hopscotch_collection(curl_commands_text: str) -> dict:
    """
    Generate a hopscotch collection from the provided curl commands text.
    - For non-login requests, adds a normalized Authorization header.
    - Replaces the base URL "https://pre-prod-api.myalice.ai" with <<PRE_PROD_URL>>.
    - Strips query parameters from the endpoint and adds them as header entries.
    - If duplicate request names are encountered, only the first occurrence is kept.
    """
    curl_commands = re.split(r"(?m)^(?=curl )", curl_commands_text)
    curl_commands = [cmd.strip() for cmd in curl_commands if cmd.strip()]

    requests_list = []
    seen_names = set()

    for idx, cmd in enumerate(curl_commands, start=1):
        parsed = parse_curl(cmd)
        method = parsed["method"].upper()
        original_endpoint = parsed["endpoint"]

        # Process the endpoint URL: remove query parameters.
        endpoint_clean, query_headers = process_endpoint(original_endpoint)
        # Replace the base URL with <<PRE_PROD_URL>>.
        if endpoint_clean and endpoint_clean.startswith(
            "https://pre-prod-api.myalice.ai"
        ):
            endpoint_clean = endpoint_clean.replace(
                "https://pre-prod-api.myalice.ai", "<<PRE_PROD_URL>>"
            )

        # Derive the request name.
        name = derive_request_name(original_endpoint, idx)
        if name in seen_names:
            continue  # Skip duplicate names.
        seen_names.add(name)

        # Determine if this is a login request.
        is_login = original_endpoint and "login" in original_endpoint.lower()

        # Extract the Authorization header value (if any).
        auth_value = None
        for h in parsed["headers"]:
            if h["name"].lower() == "authorization":
                auth_value = h["value"]
                break

        formatted_auth_header = None
        if not is_login:
            if auth_value is None:
                auth_value = ""
            else:
                auth_value = normalize_authorization(auth_value)
            formatted_auth_header = {
                "key": "Authorization",
                "value": auth_value,
                "active": True,
                "description": "",
            }

        # Prepare the body object.
        if method == "GET":
            body_obj = {"contentType": None, "body": None}
        else:
            content_type = ""
            for h in parsed["headers"]:
                if h["name"].lower() == "content-type":
                    content_type = h["value"]
                    break
            body_obj = {"contentType": content_type, "body": parsed["body"]}

        request_obj = {
            "v": "11",
            "name": name,
            "method": method,
            "endpoint": endpoint_clean,
            "params": [],
            "headers": [],
            "preRequestScript": "",
            "testScript": "",
            "auth": {"authType": "inherit", "authActive": True},
            "body": body_obj,
            "requestVariables": [],
            "responses": {},
        }
        if not is_login and formatted_auth_header is not None:
            request_obj["headers"].append(formatted_auth_header)
        if query_headers:
            request_obj["headers"].extend(query_headers)

        requests_list.append(request_obj)

    collection = {
        "v": 6,
        "name": "Inbox",
        "folders": [],
        "requests": requests_list,
        "auth": {"authType": "none", "authActive": True},
        "headers": [],
        "_ref_id": "coll_" + uuid.uuid4().hex,
    }
    return collection


def main():
    input_filename = "curl.txt"
    try:
        with open(input_filename, "r", encoding="utf-8") as f:
            curl_commands_text = f.read()
    except FileNotFoundError:
        print(f"File '{input_filename}' not found.")
        return

    collection = generate_hopscotch_collection(curl_commands_text)

    output_filename = "output.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2)

    print(f"JSON output saved to {output_filename}")


if __name__ == "__main__":
    main()
