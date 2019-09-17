def remove_empty_list_item(string_list):
    return list(filter(lambda str: str != '', [str.strip() for str in string_list]));