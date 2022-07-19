from uuid import uuid4

subscriber_table_name = "subscriber-dynamodb-table-" + str(uuid4())

dynamodb_tables = {
    f"{subscriber_table_name}": {
        "hash_key": {
            "name": "id",
            "type": "S",
        },
    }
}
