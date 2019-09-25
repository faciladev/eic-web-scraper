from sqlalchemy.orm import sessionmaker
from eic_scraper.models import NewsEventModel, IncentiveModel, SectorModel, CountryProfileModel, ChinesePageModel,ServiceModel, db_connect, create_tables
from eic_scraper.items import NewsEventItem, IncentiveItem, SectorItem, CountryProfileItem, ServiceItem, ChinesePageItem

class StoreInDbPipeline(object):

    def __init__(self):
        engine = db_connect()
        create_tables(engine)
        self.Session = sessionmaker(bind=engine)


    def process_item(self, item, spider):
        return self.save_model(item, spider)

    def save_model(self, item, spider):
        session = self.Session()

        model_instance = None;
        if isinstance(item, NewsEventItem):
            model_instance = NewsEventModel(**item)
        elif isinstance(item, IncentiveItem):
            model_instance = IncentiveModel(**item)
        elif isinstance(item, SectorItem):
            model_instance = SectorModel(**item)
        elif isinstance(item, CountryProfileItem):
            model_instance = CountryProfileModel(**item)
        elif isinstance(item, ServiceItem):
            model_instance = ServiceModel(**item)
        elif isinstance(item, ChinesePageItem):
            model_instance = ChinesePageModel(**item)

        try:
            session.add(model_instance)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item
