import scrapy
import json
# from scrapy_splash import SplashRequest

from eic_scraper.items import ServiceItem
from eic_scraper.utils import remove_empty_list_item

class  ServiceSpider(scrapy.Spider):
    name = "service_site"
    allowed_domains = ['invest-ethiopia.com']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        self.SERVICES = {
            'url': 'http://www.invest-ethiopia.com/api/services',
            'initial_parser': self.parse_services
        }

    def start_requests(self):
        item_maps = [
            self.SERVICES
        ]

        for item_map in item_maps:
            yield scrapy.Request(url=item_map['url'], callback=item_map['initial_parser'])

    def parse_services(self, response):
        services = json.loads(response.body)
        
        for service in services:
            for item in self.parse_service(service):
                yield item
            

            

    def parse_service(self, service):

        def parse_requirement(response):
            requirements = json.loads(response.body)

            item = ServiceItem()
            item['ServiceId'] = service['ServiceId']
            item['Name'] = service['Name']
            item['NameEnglish'] = service['NameEnglish']
            item['DisplayName'] = service['DisplayName']
            item['DisplayNameEnglish'] = service['DisplayNameEnglish']
            item['Abbreviation'] = service['Abbreviation']
            item['Requirements'] = requirements
            print('item', item)
            yield item
        
        service_id = service['ServiceId']
        url = f'http://www.invest-ethiopia.com/api/servicePrerequisiteByServiceId/{service_id}'

        yield scrapy.Request(url=url, callback=parse_requirement)

