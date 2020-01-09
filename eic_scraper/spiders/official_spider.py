import scrapy
import collections
import json
from scrapy_splash import SplashRequest

from eic_scraper.items import NewsEventItem, IncentiveItem, SectorItem, CountryProfileItem
from eic_scraper.utils import remove_empty_list_item


class OfficialSiteSpider(scrapy.Spider):
    name = "official_site"
    allowed_domains = ['investethiopia.gov.et']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.NEWS_EVENT_MAP = {
            'url': 'http://www.investethiopia.gov.et/index.php/information-center/news-and-events.html',
            'initial_parser': self.parse_news_event_listing
        }

        self.INCENTIVE_MAP = {
            'url': 'http://www.investethiopia.gov.et/index.php/investment-process/incentive-package.html',
            'initial_parser': self.parse_incentive_packages
        }

        self.SECTOR_MAP = [
            {
                'url': 'http://www.investethiopia.gov.et/index.php/investment-opportunities/strategic-sectors/leather-shoes-and-leather-products.html',
                'initial_parser': self.parse_sector_leather
            },
            {
                'url': 'http://www.investethiopia.gov.et/index.php/investment-opportunities/strategic-sectors/textiles-and-garments.html',
                'initial_parser': self.parse_sector_textile
            },
            {
                'url': 'http://www.investethiopia.gov.et/index.php/investment-opportunities/strategic-sectors/horticulture.html',
                'initial_parser': self.parse_sector_horticulture
            },
            {
                'url': 'http://www.investethiopia.gov.et/index.php/investment-opportunities/strategic-sectors/agriculture.html',
                'initial_parser': self.parse_sector_argriculture
            },
            {
                'url': 'http://www.investethiopia.gov.et/index.php/investment-opportunities/strategic-sectors/construction.html',
                'initial_parser': self.parse_sector_construction
            },
            {
                'url': 'http://www.investethiopia.gov.et/index.php/investment-opportunities/strategic-sectors/tourism.html',
                'initial_parser': self.parse_sector_tourism
            },
            {
                'url': 'http://www.investethiopia.gov.et/index.php/investment-opportunities/strategic-sectors/manufacturing.html',
                'initial_parser': self.parse_sector_manufacturing
            },
            {
                'url': 'http://www.investethiopia.gov.et/index.php/investment-opportunities/strategic-sectors/pharmaceuticals.html',
                'initial_parser': self.parse_sector_pharmaceuticals
            },
            {
                'url': 'http://www.investethiopia.gov.et/index.php/investment-opportunities/strategic-sectors/power.html',
                'initial_parser': self.parse_sector_power
            },
            {
                'url': 'http://www.investethiopia.gov.et/index.php/investment-opportunities/strategic-sectors/agro-processing.html',
                'initial_parser': self.parse_sector_agro_process
            }
        ]

        self.ECONOMIC_INDICATOR_MAP = {
            'url': 'http://www.investethiopia.gov.et/index.php/why-ethiopia/economic-indicators.html',
            'initial_parser': self.parse_economic_indicator
        }

    def start_requests(self):
        item_maps = [
            # self.NEWS_EVENT_MAP,
            self.INCENTIVE_MAP,
            self.SECTOR_MAP,
            self.ECONOMIC_INDICATOR_MAP
        ]
        for item_map in item_maps:
            if type(item_map) is list:
                for inner_item_map in item_map:
                    yield SplashRequest(url=inner_item_map['url'], callback=inner_item_map['initial_parser'])
            else:
                yield SplashRequest(url=item_map['url'], callback=item_map['initial_parser'])

    def parse_news_event_listing(self, response):
        items = response.css('.article-intro')
        for item in items:
            link = item.xpath('.//a[@itemprop="url"]/@href').get()
            yield response.follow(link, callback=self.parse_news_event_detail)

        next_page = response.xpath('//a[@title="Next"]/@href').get()
        if(next_page is not None):
            yield response.follow(next_page, callback=self.parse_news_event_listing)

    def parse_news_event_detail(self, response):
        item = response.xpath('//article')

        image = item.xpath('.//img/@src').get()
        title = item.css('.article-title::text').get().strip()
        url = response.url
        published = item.xpath(
            './/time[@itemprop="datePublished"]/text()').get().strip()
        content = remove_empty_list_item(item.xpath(
            './/p/descendant-or-self::*/text()').getall())

        news_event_item = NewsEventItem(
            image=image,
            title=title,
            url=url,
            published=published,
            content=content
        )

        yield news_event_item

    def parse_incentive_packages(self, response):
        heading_container = response.css('ul.sprocket-tabs-nav')
        package_headings = remove_empty_list_item(
            heading_container.xpath('.//li/descendant-or-self::*/text()').getall())
        package_bodies = response.css('div.sprocket-tabs-panel')

        for index_body, body in enumerate(package_bodies):
            readmore = body.css('a.readon').attrib['href']
            if readmore is not None:
                yield response.follow(readmore if readmore.startswith('http') else 'http://www.' + self.allowed_domains[0] + readmore, callback=self.parse_incentives)
            else:
                incentives = body.xpath('.//tbody/tr')
                for index_incentive, incentive in enumerate(incentives):
                    item_fields = incentive.xpath('.//td')

                    item = IncentiveItem()
                    item['name'] = remove_empty_list_item(
                        item_fields[0].xpath('.//descendant-or-self::*/text()').getall())
                    item['description'] = remove_empty_list_item(
                        item_fields[1].xpath('.//descendant-or-self::*/text()').getall())
                    item['legal_reference'] = remove_empty_list_item(
                        item_fields[2].xpath('.//descendant-or-self::*/text()').getall())
                    item['law_section'] = remove_empty_list_item(
                        item_fields[3].xpath('.//descendant-or-self::*/text()').getall())
                    item['sector'] = remove_empty_list_item(
                        item_fields[4].xpath('.//descendant-or-self::*/text()').getall())
                    item['eligebility'] = remove_empty_list_item(
                        item_fields[5].xpath('.//descendant-or-self::*/text()').getall())
                    item['rewarding_authority'] = remove_empty_list_item(
                        item_fields[6].xpath('.//descendant-or-self::*/text()').getall())
                    item['implementing_authority'] = remove_empty_list_item(
                        item_fields[7].xpath('.//descendant-or-self::*/text()').getall())
                    item['incentive_package'] = package_headings[index_body]

                    yield item

    def parse_incentives(self, response):
        incentives_container = response.css('section.article-content')

        for incentive in incentives_container.xpath('.//tbody/tr'):
            item_fields = incentive.xpath('.//td')

            item = IncentiveItem()
            item['name'] = remove_empty_list_item(
                item_fields[0].xpath('.//descendant-or-self::*/text()').getall())
            item['description'] = remove_empty_list_item(
                item_fields[1].xpath('.//descendant-or-self::*/text()').getall())
            item['legal_reference'] = remove_empty_list_item(
                item_fields[2].xpath('.//descendant-or-self::*/text()').getall())
            item['law_section'] = remove_empty_list_item(
                item_fields[3].xpath('.//descendant-or-self::*/text()').getall())
            item['sector'] = remove_empty_list_item(
                item_fields[4].xpath('.//descendant-or-self::*/text()').getall())
            item['eligebility'] = remove_empty_list_item(
                item_fields[5].xpath('.//descendant-or-self::*/text()').getall())
            item['rewarding_authority'] = remove_empty_list_item(
                item_fields[6].xpath('.//descendant-or-self::*/text()').getall())
            item['implementing_authority'] = remove_empty_list_item(
                item_fields[7].xpath('.//descendant-or-self::*/text()').getall())
            item['incentive_package'] = response.xpath(
                '//h1[@class="article-title"]/text()').get().strip()

            yield item

    def parse_sector_leather(self, response):
        sector_content = collections.OrderedDict()
        section_headers = response.xpath('//h3')
        for header_index, header in enumerate(section_headers):
            content = None
            lists = []
            if header_index == 0:
                lists = remove_empty_list_item(header.xpath(
                    './/following-sibling::ul[1]/li/text() | .//following-sibling::ul[2]/li/text()').getall())
            elif header_index == 4:
                organisations = header.xpath(
                    './/following-sibling::p/strong/parent::p')
                organisation_address_map = {}
                for organisation in organisations:
                    address = remove_empty_list_item(organisation.xpath(
                        './/following-sibling::p[1]/descendant-or-self::*[not(self::script)]/text()').getall())
                    organisation_name = organisation.xpath(
                        './/text()').get().strip()
                    organisation_address_map[organisation_name] = address

                content = organisation_address_map
            else:
                lists = remove_empty_list_item(header.xpath(
                    './/following-sibling::ul[1]/li/text()').getall())

            if len(lists) > 0:
                content = {'lists': [{'list': lists}]}

            key = header.xpath('.//text()').get().strip()
            sector_content[key] = content

        sector_quotes = parse_sector_quotes(
            response.css('.sprocket-quotes-text'))
        if sector_quotes:
            sector_content['Success Stories'] = sector_quotes

        item = SectorItem()
        item['name'] = response.css('.article-title::text').get().strip()
        item['url'] = response.url
        item['image'] = response.css('img.article_image').attrib['src']
        item['content'] = json.dumps(sector_content)

        yield item

    def parse_sector_textile(self, response):
        sector_content = collections.OrderedDict()
        section_headers = response.xpath('//h3')
        for header_index, header in enumerate(section_headers):
            content = None
            lists = []
            if header_index == 4:
                organisations = header.xpath(
                    './/following-sibling::p/strong/parent::p')
                organisation_address_map = {}
                for organisation_index, organisation in enumerate(organisations):
                    address = None
                    if organisation_index == 1:
                        paragraphs = organisation.xpath(
                            './/following-sibling::p[1] | .//following-sibling::p[2]')
                        address = remove_empty_list_item(paragraphs.xpath(
                            './/descendant-or-self::*[not(self::script)]/text()').getall())
                    else:
                        address = remove_empty_list_item(organisation.xpath(
                            './/following-sibling::p[1]/descendant-or-self::*[not(self::script)]/text()').getall())

                    organisation_name = organisation.xpath(
                        './/text()').get().strip()
                    organisation_address_map[organisation_name] = address

                content = organisation_address_map
            else:
                lists = remove_empty_list_item(header.xpath(
                    './/following-sibling::ul[1]/li/text()').getall())

            if len(lists) > 0:
                content = {'lists': [{'list': lists}]}

            key = header.xpath('.//text()').get().strip()
            sector_content[key] = content

        sector_quotes = parse_sector_quotes(
            response.css('.sprocket-quotes-text'))
        if sector_quotes:
            sector_content['Success Stories'] = sector_quotes

        item = SectorItem()
        item['name'] = response.css('.article-title::text').get().strip()
        item['url'] = response.url
        item['image'] = response.css('img.article_image').attrib['src']
        item['content'] = json.dumps(sector_content)

        yield item

    def parse_sector_horticulture(self, response):
        sector_content = collections.OrderedDict()
        section_headers = response.xpath(
            '//h3[1] | //h3[2] | //h3[3] | //h3[4]')
        section_headers.append(section_headers.xpath(
            './/following-sibling::p/strong/parent::p')[0])

        for header_index, header in enumerate(section_headers):
            content = None
            if header_index == 2:
                content = parse_sector_quotes(header.xpath(
                    './/following-sibling::table/tbody/tr/td'))
            elif header_index == 3:
                organisations = header.xpath(
                    './/following-sibling::p/strong/parent::p')
                organisation_address_map = {}
                for organisation_index, organisation in enumerate(organisations):
                    address = remove_empty_list_item(organisation.xpath(
                        './/following-sibling::p[1]/descendant-or-self::*[not(self::script)]/text()').getall())

                    organisation_name = organisation.xpath(
                        './/text()').get().strip()
                    organisation_address_map[organisation_name] = address

                content = organisation_address_map
            elif header_index == 4:
                content = {}
                opportunity_headers = header.xpath(
                    './/following-sibling::p/strong/parent::p')[:3]
                for opportunity_header in opportunity_headers:
                    lists = remove_empty_list_item(opportunity_header.xpath(
                        './/following-sibling::ul[1]/li/text()').getall())
                    opportunity_name = opportunity_header.xpath(
                        './/text()').get().strip()

                    opportunity = {'lists': [{'list': lists}]}

                    content[opportunity_name] = opportunity
            else:
                lists = remove_empty_list_item(header.xpath(
                    './/following-sibling::ul[1]/li/text()').getall())
                content = {'lists': [{'list': lists}]}

            key = header.xpath('.//text()').get().strip()
            sector_content[key] = content

        item = SectorItem()
        item['name'] = response.css('.article-title::text').get().strip()
        item['url'] = response.url
        item['image'] = response.css('img.article_image').attrib['src']
        item['content'] = json.dumps(sector_content)

        yield item

    def parse_sector_argriculture(self, response):
        sector_content = remove_empty_list_item(response.css(
            '.article-content').xpath('.//ul/li/text()').getall())

        item = SectorItem()
        item['name'] = response.css('.article-title::text').get().strip()
        item['url'] = response.url
        item['content'] = {'lists': [{'list': sector_content}]}

        yield item

    def parse_sector_construction(self, response):
        sector_content = remove_empty_list_item(response.css(
            '.article-content').xpath('.//ul/li/text()').getall())

        item = SectorItem()
        item['name'] = response.css('.article-title::text').get().strip()
        item['url'] = response.url
        item['content'] = {'lists': [{'list': sector_content}]}

        yield item

    def parse_sector_tourism(self, response):
        sector_content = remove_empty_list_item(response.css(
            '.article-content').xpath('.//ul/li/text()').getall())

        item = SectorItem()
        item['name'] = response.css('.article-title::text').get().strip()
        item['url'] = response.url
        item['content'] = {'lists': [{'list': sector_content}]}

        yield item

    def parse_sector_manufacturing(self, response):
        sector_content = collections.OrderedDict()
        section_headers = response.xpath('//h3')
        for header_index, header in enumerate(section_headers):
            content = None
            lists = []
            if header_index == 0:
                lists = remove_empty_list_item(header.xpath(
                    './/following-sibling::ul[1]/li/text() | .//following-sibling::ul[2]/li/text() | .//following-sibling::ul[3]/li/text()').getall())
            else:
                lists = remove_empty_list_item(header.xpath(
                    './/following-sibling::ul[1]/li/text()').getall())
            if len(lists) > 0:
                content = {'lists': [{'list': lists}]}

            key = header.xpath('.//text()').get().strip()
            sector_content[key] = content

        item = SectorItem()
        item['name'] = response.css('.article-title::text').get().strip()
        item['url'] = response.url
        item['content'] = json.dumps(sector_content)

        yield item

    def parse_sector_pharmaceuticals(self, response):
        sector_content = collections.OrderedDict()
        section_headers = response.xpath('//h3')
        for header_index, header in enumerate(section_headers):
            content = None
            lists = []
            if header_index == 0:
                lists = remove_empty_list_item(header.xpath(
                    './/following-sibling::p[1]/text()').getall())
            else:
                lists = remove_empty_list_item(header.xpath(
                    './/following-sibling::ul[1]/li/text()').getall())

            if len(lists) > 0:
                content = {'lists': [{'list': lists}]}

            key = header.xpath('.//text()').get().strip()
            sector_content[key] = content

        item = SectorItem()
        item['name'] = response.css('.article-title::text').get().strip()
        item['url'] = response.url
        item['content'] = json.dumps(sector_content)

        yield item

    def parse_sector_power(self, response):
        sector_content = collections.OrderedDict()
        section_headers = response.css(
            '.article-content').xpath('.//p/strong/parent::p')
        for header_index, header in enumerate(section_headers):
            content = None
            lists = []
            if header_index == 0:
                lists = remove_empty_list_item(header.xpath(
                    './/following-sibling::p/text()').getall())
            else:
                lists = remove_empty_list_item(header.xpath(
                    './/following-sibling::ul[1]/li/text()').getall())

            if len(lists) > 0:
                content = {'lists': [{'list': lists}]}

            key = header.xpath('.//text()').get().strip()
            sector_content[key] = content

        item = SectorItem()
        item['name'] = response.css('.article-title::text').get().strip()
        item['url'] = response.url
        item['content'] = json.dumps(sector_content)

        yield item

    def parse_sector_agro_process(self, response):
        sector_content = collections.OrderedDict()
        section_headers = response.css(
            '.article-content').xpath('.//p/strong/parent::p')
        for header_index, header in enumerate(section_headers):
            lists = remove_empty_list_item(header.xpath(
                './/following-sibling::ul[1]/li/text()').getall())
            key = header.xpath('.//text()').get().strip()

            sector_content[key] = {'lists': [{'list': lists}]}

        item = SectorItem()
        item['name'] = response.css('.article-title::text').get().strip()
        item['url'] = response.url
        item['content'] = json.dumps(sector_content)

        yield item

    def parse_economic_indicator(self, response):
        indicator_content = collections.OrderedDict()
        section_headers = response.css(
            '.article-content').xpath('.//p/strong/parent::p')

        for header_index, header in enumerate(section_headers):
            content = None
            lists = []
            if header_index == 0:
                lists = remove_empty_list_item(header.xpath(
                    './/following-sibling::ul[1]/li/text() | .//following-sibling::ul[2]/li/text()').getall())
            elif header_index == 4:
                lists = remove_empty_list_item(header.xpath(
                    './/following-sibling::ul[1]/li/text()').getall())
            else:
                continue

            if len(lists) > 0:
                content = {'lists': [{'list': lists}]}

            key = header.xpath('.//descendant-or-self::*/text()').get().strip()
            indicator_content.update({key: {'content': content}})
        item = CountryProfileItem()
        item['name'] = response.css('.article-title::text').get().strip()
        item['content'] = json.dumps(indicator_content)

        yield item


def parse_sector_quotes(quotes_container):
    quotes = []
    if quotes_container:
        for quote_container in quotes_container:
            text = remove_empty_list_item(quote_container.xpath(
                './/descendant-or-self::*[not(self::img)]/text()').getall())
            images = quote_container.xpath(
                './/descendant-or-self::img/@src').getall()

            quote = {'text': text, 'images': images}
            quotes.append(quote)

    return quotes
