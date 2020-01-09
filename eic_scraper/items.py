import scrapy


class NewsEventItem(scrapy.Item):
    image = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    published = scrapy.Field()
    content = scrapy.Field()


class IncentiveItem(scrapy.Item):
    name = scrapy.Field()
    description = scrapy.Field()
    legal_reference = scrapy.Field()
    law_section = scrapy.Field()
    sector = scrapy.Field()
    eligebility = scrapy.Field()
    rewarding_authority = scrapy.Field()
    implementing_authority = scrapy.Field()
    incentive_package = scrapy.Field()


class SectorItem(scrapy.Item):
    name = scrapy.Field()
    image = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()


class CountryProfileItem(scrapy.Item):
    name = scrapy.Field()
    content = scrapy.Field()


class ServiceItem(scrapy.Item):
    ServiceId = scrapy.Field()
    Name = scrapy.Field()
    NameEnglish = scrapy.Field()
    DisplayName = scrapy.Field()
    DisplayNameEnglish = scrapy.Field()
    Abbreviation = scrapy.Field()
    Requirements = scrapy.Field()


class ChinesePageItem(scrapy.Item):
    name = scrapy.Field()
    image = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    excerpt = scrapy.Field()
