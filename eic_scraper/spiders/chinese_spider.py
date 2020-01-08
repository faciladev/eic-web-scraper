import scrapy
from scrapy.http import HtmlResponse
import json

from eic_scraper.items import ChinesePageItem
from eic_scraper.utils import remove_empty_list_item, remove_list_item_by_re


class ChineseSpider(scrapy.Spider):
    name = "chinese_site"
    allowed_domains = ['cn.investethiopia.gov.et']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.PAGES = [
            {
                'eng_id': 113,
                'cn_id': 519,
                'type': 'page',
                'initial_parser': self.parse_page
            },
            {
                'eng_id': 148,
                'cn_id': 524,
                'type': 'page',
                'initial_parser': self.parse_page
            },
            {
                'eng_id': 112,
                'cn_id': 616,
                'type': 'page',
                'initial_parser': self.parse_page
            },
            {
                'eng_id': 201,
                'cn_id': 492,
                'type': 'page',
                'initial_parser': self.parse_page
            },
            {
                'eng_id': 203,
                'cn_id': 599,
                'type': 'page',
                'initial_parser': self.parse_page
            },
            {
                'eng_id': 204,
                'cn_id': 600,
                'type': 'page',
                'initial_parser': self.parse_page
            },
            {
                'eng_id': 206,
                'cn_id': 605,
                'type': 'page',
                'initial_parser': self.parse_page
            },
            {
                'eng_id': 149,
                'cn_id': 585,
                'type': 'page',
                'initial_parser': self.parse_page
            },
            {
                'eng_id': 192,
                'cn_id': 531,
                'type': 'page',
                'initial_parser': self.parse_page
            }
        ]

    def start_requests(self):
        item_maps = [
            self.PAGES
        ]

        for item_map in item_maps:
            for inner_item_map in item_map:
                url = f'http://{self.allowed_domains[0]}/wp-json/wp/v2/{inner_item_map["type"]}s/{inner_item_map["eng_id"]}'
                yield scrapy.Request(url=url, callback=inner_item_map['initial_parser'])

    def parse_page(self, response):
        page = json.loads(response.body)

        def parse_featured_media(media_response):
            image = json.loads(media_response.body)

            html_response = HtmlResponse(response.url, body=bytes(
                page['content']['rendered'], 'utf-8'))

            section_titles = html_response.xpath('//h2 | //h1')
            following_nodes = section_titles[0].xpath(
                './/following-sibling::*')
            content = {}
            for index, section_title in enumerate(section_titles):
                if section_title.xpath('.//descendant-or-self::*/text()').get() == None:
                    continue

                next_index = index + 1 if index + \
                    1 < len(section_titles) else index
                section_nodes = self.parse_between_nodes(
                    section_title, section_titles[next_index])
                title = section_title.xpath(
                    './/descendant-or-self::*/text()').get().strip()
                content.update({title: section_nodes})
            item = ChinesePageItem()
            item['name'] = page['title']['rendered']
            item['url'] = page['link']
            excerpt = HtmlResponse(response.url, body=bytes(
                page['excerpt']['rendered'], 'utf-8'))
            item['excerpt'] = escape_wordpress_vc(
                excerpt.xpath('//descendant-or-self::*/text()').getall())
            item['content'] = content
            item['image'] = image['link']
            yield item

        url = f'http://{self.allowed_domains[0]}/wp-json/wp/v2/media/{page["featured_media"]}'
        yield scrapy.Request(url=url, callback=parse_featured_media)

    def parse_between_nodes(self, start, end):
        following_nodes = start.xpath('.//following-sibling::*')
        between_nodes = []

        for node in following_nodes:
            if node.get() == end.get():
                break

            # Exclude lists and tables
            node_content = node.xpath(
                './/descendant-or-self::*[not(ancestor::ul)][not(ancestor::ol)][not(ancestor::table)]/text()').getall()

            node_content = escape_wordpress_vc(node_content)

            if len(node_content) > 0:
                between_nodes.append(node_content)

            section_lists = node.xpath(
                './/descendant-or-self::ul | .//descendant-or-self::ol')

            lists = extract_lists(section_lists)

            if len(lists) > 0:
                between_nodes.append({'lists': lists})

            section_tables = node.xpath('.//descendant-or-self::table')

            tables = extract_tables(section_tables)

            if len(tables) > 0:
                between_nodes.append({'tables': tables})

        return between_nodes


def extract_lists(section_lists):
    lists = []
    for section_list in section_lists:
        list_content = remove_empty_list_item(
            section_list.xpath('.//li/descendant-or-self::*/text()').getall())
        if len(list_content) > 0:
            lists.append({'list': list_content})

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


def escape_wordpress_vc(node_content):
    return remove_empty_list_item(remove_list_item_by_re(r'(\[/?vc_.*?\])', node_content))
