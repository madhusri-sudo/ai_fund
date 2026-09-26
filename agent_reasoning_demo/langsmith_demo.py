from langsmith import traceable


@traceable(
    name="IT Support Request"
)
def process_request(query: str):

    print(f"Processing request: {query}")

    if "vpn" in query.lower():

        return "VPN troubleshooting requested."

    if "password" in query.lower():

        return "Password reset requested."

    return "Unknown support request."


if __name__ == "__main__":

    result = process_request(
        "hii"
    )

    print(result)