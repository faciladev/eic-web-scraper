import scrapy
import collections
import json

from eic_scraper.items import CountryProfileItem
from eic_scraper.utils import remove_empty_list_item, extract_tables, extract_lists


class IGuideSpider(scrapy.Spider):
    name = "iguide_site"
    allowed_domains = ['theiguides.org']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.COUNTRY_PROFILE_MAP = {
            'url': 'https://www.theiguides.org/public-docs/guides/ethiopia',
            'initial_parser': self.parse_country_profiles
        }

    def start_requests(self):
        item_maps = [
            self.COUNTRY_PROFILE_MAP
        ]

        for item_map in item_maps:
            yield scrapy.Request(url=item_map['url'], callback=item_map['initial_parser'])

    def parse_country_profiles(self, response):

        profiles = response.xpath('//div[@id="TabsContent"]/div')
        for index_profile, profile in enumerate(profiles):
            profile_id = profile.xpath('.//@id').get().strip()
            section_link_divs = None
            menu_id = None

            if profile_id == 'tabGetStarted':
                menu_id = 'menuTab_GetStarted'
            elif profile_id == 'tabLabour':
                menu_id = 'menuTab_Labour'
            elif profile_id == 'tabProductionFactors':
                menu_id = 'menuTab_ProductionFactors'
            elif profile_id == 'tabLand':
                menu_id = 'menuTab_Land'
            elif profile_id == 'tabTaxes':
                menu_id = 'menuTab_Taxes'
            elif profile_id == 'tabProtectYourInvestment':
                menu_id = 'menuTab_ProtectYourInvestment'
            elif profile_id == 'tabHome':
                menu_id = 'menuTab_Home'
            elif profile_id == 'tabGrowthSectorsAndOpportunities':
                menu_id = 'menuTab_GrowthSectorsAndOpportunities'
            else:
                continue

            section_link_divs = profile.xpath(
                f'.//div[@id="{menu_id}"]').css('.accordion-group')
            yield parse_country_profile(response, profile_id, section_link_divs)


def parse_country_profile(response, profile_id, section_link_divs):
    section_link_maps = collections.OrderedDict()

    for section_link_div in section_link_divs:
        section_links = section_link_div.xpath('.//a/text()/parent::a')
        for section_link in section_links:
            href = section_link.attrib['href']
            title = section_link.xpath('.//text()').get().strip()
            if "collapse" in href:
                href = section_link.xpath(
                    './/following-sibling::a/@href').get()

            section_link_maps[title] = href

    section_content_ids = list(section_link_maps.values())
    section_titles = list(section_link_maps.keys())

    sections = collections.OrderedDict()
    for index in range(0, len(section_content_ids)):
        print(section_content_ids[index])
        id = section_content_ids[index].replace('#', '')
        section_images = response.xpath(
            f'//div[@id="{id}"]/div/*/descendant-or-self::img/@src').getall()

        # Exclude tables and lists
        section_text = remove_empty_list_item(response.xpath(
            f'//div[@id="{id}"]/*/descendant-or-self::*[not(self::iframe)][not(ancestor::ul)][not(ancestor::ol)][not(ancestor::table)]/text()').getall())

        section_lists = response.xpath(
            f'//div[@id="{id}"]/descendant-or-self::ul | //div[@id="{id}"]/descendant-or-self::ol')

        lists = extract_lists(section_lists)

        if len(lists) > 0:
            section_text.append({'lists': lists})

        section_tables = response.xpath(
            f'//div[@id="{id}"]/descendant-or-self::table')

        tables = extract_tables(section_tables)

        if len(tables) > 0:
            section_text.append({'tables': tables})

        sections[section_titles[index]] = {
            'images': section_images, 'content': section_text}

    item = CountryProfileItem()
    item['name'] = response.xpath(
        f'//ul[@id="Tabs"]/li/a[@href="#{profile_id}"]/text()').get().strip()
    item['content'] = json.dumps(sections)

    return item
