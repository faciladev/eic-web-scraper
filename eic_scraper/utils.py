import re


def remove_empty_list_item(string_list):
    return list(filter(lambda str: str != '', [str.strip() for str in string_list]))


def remove_list_item_by_re(regexp, string_list):
    return list(map(lambda str: re.sub(regexp, '', str), string_list))


def extract_lists(section_lists):
    lists = []
    for section_list in section_lists:
        lis = section_list.xpath('.//li')
        single_list = []
        for li in lis:
            list_content = remove_empty_list_item(
                li.xpath('.//descendant-or-self::*/text()').getall())
            single_list.append(" ".join(list_content))

        if len(single_list) > 0:
            lists.append({'list': single_list})

    return lists


def extract_tables(section_tables):
    tables = []
    for section_table in section_tables:
        table = {'headers': [], 'rows': []}
        headers = section_table.xpath('.//th')
        for header in headers:
            table['headers'].append(
                header.xpath('.//descendant-or-self::*/text()').get(default=""))

        rows = section_table.xpath('.//tbody/tr')
        for row in rows:
            row_content = remove_empty_list_item(
                row.xpath('.//td/descendant-or-self::*/text()').getall())
            table['rows'].append(row_content)

        tables.append({'table': table})

    return tables
