import re
import shlex
import json
import uuid


def parse_curl(curl_command):
    """
    Parse a single curl command and return a dictionary with:
      - method
      - endpoint (URL)
      - headers (a list of {name, value} dicts)
      - body (raw data string or empty string)
    """
    # Remove backslash-newline continuations and extra spaces.
    command = curl_command.replace("\\\n", " ").strip()

    # Try using shlex.split with default (posix=True) and if error occurs, fall back to posix=False.
    try:
        tokens = shlex.split(command)
    except ValueError as e:
        # Fallback: use posix=False which is less strict about quotes.
        tokens = shlex.split(command, posix=False)

    # Initialize values.
    url = None
    method = None
    headers = []
    data = None

    # The first token should be "curl"
    i = 1
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
            # Remove leading $ if present.
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
            # Split header line into key and value.
            if ": " in header_line:
                key, value = header_line.split(": ", 1)
            elif ":" in header_line:
                key, value = header_line.split(":", 1)
            else:
                key, value = header_line, ""
            headers.append({"name": key.strip(), "value": value.strip()})
        i += 1

    # If method is not set, assume POST if there's data, otherwise GET.
    if method is None:
        method = "POST" if data is not None else "GET"

    return {
        "method": method,
        "endpoint": url,
        "headers": headers,
        "body": data if data is not None else "",
    }


def generate_hopscotch_collection(curl_commands_text):
    """
    Given a multi-line string with one or more curl commands,
    parse each one and return a dictionary in the hopscotch collection format.
    For non-login requests, an Authorization header is always added.
    Also, the base URL "https://pre-prod-api.myalice.ai" is replaced with <<BASE_URL>>.
    """
    # Split the text into individual curl commands.
    curl_commands = re.split(r"(?m)^(?=curl )", curl_commands_text)
    curl_commands = [cmd.strip() for cmd in curl_commands if cmd.strip()]

    requests_list = []
    for idx, cmd in enumerate(curl_commands, start=1):
        parsed = parse_curl(cmd)
        method = parsed["method"].upper()

        # Replace the base URL if present.
        endpoint = parsed["endpoint"]
        if endpoint and endpoint.startswith("https://pre-prod-api.myalice.ai"):
            endpoint = endpoint.replace(
                "https://pre-prod-api.myalice.ai", "<<STAGE_URL>>"
            )

        # Derive a name from the original endpoint (using the last segment) or a generic one.
        if parsed["endpoint"]:
            name = parsed["endpoint"].rstrip("/").split("/")[-1]
        else:
            name = f"Request {idx}"

        # Determine if this is a login request.
        is_login = parsed["endpoint"] and "login" in parsed["endpoint"].lower()

        # Find the Authorization header value from the parsed headers (if any).
        auth_header_value = None
        for h in parsed["headers"]:
            if h["name"].lower() == "authorization":
                auth_header_value = h["value"]
                break

        # For all non-login requests, ensure an Authorization header is added.
        formatted_auth_header = None
        if not is_login:
            if auth_header_value is None:
                auth_header_value = ""  # Default to empty if not provided.
            formatted_auth_header = {
                "key": "Authorization",
                "value": auth_header_value,
                "active": True,
                "description": "",
            }

        # Prepare the body object.
        if method == "GET":
            body_obj = {"contentType": None, "body": None}
        else:
            # For non-GET, find content-type if provided.
            content_type = ""
            for h in parsed["headers"]:
                if h["name"].lower() == "content-type":
                    content_type = h["value"]
                    break
            body_obj = {"contentType": content_type, "body": parsed["body"]}

        # Build the request object.
        request_obj = {
            "v": "11",
            "name": name,
            "method": method,
            "endpoint": endpoint,
            "params": [],
            "headers": [],
            "preRequestScript": "",
            "testScript": "",
            "auth": {"authType": "inherit", "authActive": True},
            "body": body_obj,
            "requestVariables": [],
            "responses": {},
        }

        # Add the Authorization header for non-login requests.
        if formatted_auth_header is not None:
            request_obj["headers"].append(formatted_auth_header)

        requests_list.append(request_obj)

    # Build the final hopscotch collection object.
    collection = {
        "v": 6,
        "name": "Converted Collection",
        "folders": [],
        "requests": requests_list,
        "auth": {"authType": "none", "authActive": True},
        "headers": [],
        "_ref_id": "coll_" + uuid.uuid4().hex,
    }

    return collection


def main():
    # Read the curl commands from the file "curl.txt"
    input_filename = "curl.txt"
    try:
        with open(input_filename, "r", encoding="utf-8") as f:
            curl_commands_text = f.read()
    except FileNotFoundError:
        print(f"File '{input_filename}' not found.")
        return

    collection = generate_hopscotch_collection(curl_commands_text)

    # Save the JSON output to a file named "output.json"
    output_filename = "output.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2)

    print(f"JSON output saved to {output_filename}")


if __name__ == "__main__":
    main()
