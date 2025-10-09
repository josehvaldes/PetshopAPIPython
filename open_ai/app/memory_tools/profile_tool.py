#TODO to delete this file if not used later
"""Milvus vector database integration tool."""


user_profile_tool = {
    "name": "user_profile_lookup",
    "description": "Fetches user profile information from Storage account table",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "The ID of the user"}
        },
        "required": ["user_id"]
    }
}

def user_profile_lookup(user_id: str):
    # Query Storace account for user data
    # TODO create the table in the Storage Account
    row = "TODO"
    return dict(row) if row else {"error": "User not found"}
