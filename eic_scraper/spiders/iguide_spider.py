import scrapy

from eic_scraper.items import CountryProfileItem
from eic_scraper.utils import remove_empty_list_item

class  IGuideSpider(scrapy.Spider):
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
            
            section_link_divs = profile.xpath(f'.//div[@id="{menu_id}"]').css('.accordion-group')
            yield parse_country_profile(response, profile_id, section_link_divs)


def parse_country_profile(response, profile_id, section_link_divs):
    section_link_maps = {}
    for section_link_div in section_link_divs:
        section_links = section_link_div.xpath('.//a/text()/parent::a')
        for section_link in section_links:
            href = section_link.attrib['href'] 
            title = section_link.xpath('.//text()').get().strip()
            if "collapse" in href:
                href = section_link.xpath('.//following-sibling::a/@href').get()

            section_link_maps[title] = href
    
    section_content_ids = section_link_maps.values()
    section_titles = section_link_maps.keys()

    section_contents = []
    for section_content_id in section_content_ids:
        id = section_content_id.replace('#', '')
        section_images = response.xpath(f'//div[@id="{id}"]/div/*/descendant-or-self::img/@src').getall()
        section_text = remove_empty_list_item(response.xpath(f'//div[@id="{id}"]/*/descendant-or-self::*[not(self::iframe)]/text()').getall())
        
        section_contents.append({'images': section_images, 'content': section_text})

    sections = dict(zip(section_titles, section_contents))

    item = CountryProfileItem()
    item['name'] = response.xpath(f'//ul[@id="Tabs"]/li/a[@href="#{profile_id}"]/text()').get().strip()
    item['content'] = sections

    return item