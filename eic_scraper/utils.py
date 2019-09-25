import re

def remove_empty_list_item(string_list):
    return list(filter(lambda str: str != '', [str.strip() for str in string_list]))

def remove_list_item_by_re(regexp, string_list):
    return list(map(lambda str: re.sub(regexp, '', str), string_list))