import os
import request



def box_op(metadata, connection_config):
    auth_data = connection_config["auth_data"]
    client = get_box_client(auth_data)
    file = client.file(file_id=metadata["id"]).get()
    folder_path = compile_folder_path(file)
    property_values = compile_properties(file)
    file_name = file.name
    file_format = file_name.split(".")[-1]
    blob_path = ""
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        file.download_to(temp_file)
        try:
            temp_file.seek(0)
        except Exception as e:
            pass
        
        blob_path = upload_to_bucket(
            temp_file.name, f"{connection_config['id']}/{metadata['id']}/{metadata['id']}.{file_format}"
        )
    
    file_properties = {
        "source_path": f"https://app.box.com/file/{metadata['id']}",
        "folder_path": folder_path,
        "name": file_name,
        "metadata": property_values,
    }
    path = upload_dict_as_json(
        f"{connection_config['id']}/{metadata['id']}/{metadata['id']}.json",
        file_properties,
    )
    return { "file_id": metadata['id'], "blob": blob_path, "metadata": path, "source": "box", "source_ref": file_properties["source_path"] }

