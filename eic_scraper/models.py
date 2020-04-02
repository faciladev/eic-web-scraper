from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from sqlalchemy.dialects.postgresql.json import JSONB

import eic_scraper.settings as settings


DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))


def create_tables(engine):
    DeclarativeBase.metadata.create_all(engine)


class NewsEventModel(DeclarativeBase):
    __tablename__ = "news_events"

    id = Column(Integer, primary_key=True)
    image = Column('image', String, nullable=True)
    title = Column('title', String)
    url = Column('url', String)
    content = Column('content', JSONB)
    published = Column('published', DateTime)


class IncentiveModel(DeclarativeBase):
    __tablename__ = "incentives"

    id = Column(Integer, primary_key=True)
    name = Column('name', ARRAY(String), nullable=True)
    description = Column('description', ARRAY(String), nullable=True)
    legal_reference = Column('legal_reference', ARRAY(String), nullable=True)
    law_section = Column('law_section', ARRAY(String), nullable=True)
    sector = Column('sector', ARRAY(String), nullable=True)
    eligebility = Column('eligebility', ARRAY(String), nullable=True)
    rewarding_authority = Column(
        'rewarding_authority', ARRAY(String), nullable=True)
    implementing_authority = Column(
        'implementing_authority', ARRAY(String), nullable=True)
    incentive_package = Column('incentive_package', String)


class SectorModel(DeclarativeBase):
    __tablename__ = "sectors"

    id = Column(Integer, primary_key=True)
    image = Column('image', String, nullable=True)
    name = Column('name', String)
    url = Column('url', String)
    content = Column('content', JSONB)


class CountryProfileModel(DeclarativeBase):
    __tablename__ = "country_profiles"

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    content = Column('content', JSONB)


class ServiceModel(DeclarativeBase):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    ServiceId = Column('ServiceId', String)
    Name = Column('Name', String)
    NameEnglish = Column('NameEnglish', String)
    DisplayName = Column('DisplayName', String)
    DisplayNameEnglish = Column('DisplayNameEnglish', String)
    Abbreviation = Column('Abbreviation', String)
    Requirements = Column('Requirements', JSONB, nullable=True)


class ChinesePageModel(DeclarativeBase):
    __tablename__ = "chinese_page"

    id = Column(Integer, primary_key=True)
    image = Column('image', String, nullable=True)
    name = Column('name', String)
    url = Column('url', String)
    excerpt = Column('excerpt', String)
    content = Column('content', JSONB)
