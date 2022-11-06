from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    ForeignKey,
    String,
)

from sqlalchemy.orm import (
    relationship
)

Base = declarative_base()


class LocationTable(Base):
    __tablename__ = 'location'

    location_id = Column(
        Integer,
        primary_key=True
    )

    country_id = Column(
        Integer,
        ForeignKey("country.country_id")
    )

    state_id = Column(
        Integer,
        ForeignKey("state.state_id")
    )

    country = relationship(
        "CountryTable", back_populates="location"
    )

    state = relationship(
        "StateTable", back_populates='location'
    )

    lob = relationship(
        "LOBTable", back_populates="location"
    )

    def __repr__(self):
        return "LocationTable(" \
               "country_id='%s', " \
               "state_id='%s'" \
               ")>" % (
                   self.country_id,
                   self.state_id
               )


class CountryTable(Base):
    __tablename__ = 'country'

    country_id = Column(
        Integer,
        primary_key=True
    )

    project_id = Column(
        String,
        ForeignKey('project.project_id')
    )

    country_name = Column(String)

    location = relationship(
        "LocationTable", back_populates="country"
    )

    state = relationship(
        "StateTable", back_populates="country"
    )

    project = relationship(
        "ProjectTable", back_populates="country"
    )

    def __repr__(self):
        return "CountryTable(" \
               "location_id='%s', " \
               "country_name='%s', " \
               "project_id='%s', " \
               ")>" % (
                   self.location_id,
                   self.country_name,
                   self.project_id
               )


class StateTable(Base):
    __tablename__ = 'state'

    state_id = Column(
        Integer,
        primary_key=True
    )

    country_id = Column(
        Integer,
        ForeignKey("country.country_id")
    )

    project_id = Column(
        String,
        ForeignKey('project.project_id')
    )

    state_name = Column(String)

    country = relationship("CountryTable", back_populates="state")

    location = relationship("LocationTable", back_populates="state")

    project = relationship(
        "ProjectTable", back_populates="state"
    )

    def __repr__(self):
        return "StateTable(" \
               "country_id='%s'" \
               "location_id='%s'" \
               "state_name='%s', " \
               "project_id='%s', " \
               ")>" % (
                   self.country_id,
                   self.location_id,
                   self.state_name,
                   self.project_id
               )


class LOBTable(Base):
    __tablename__ = 'lob'

    lob_id = Column(
        Integer,
        primary_key=True
    )

    lob_type = Column(String)

    location_id = Column(
        Integer,
        ForeignKey('location.location_id')
    )

    project_id = Column(
        String,
        ForeignKey('project.project_id')
    )

    location = relationship(
        "LocationTable", back_populates='lob'
    )

    project = relationship(
        "ProjectTable", back_populates="lob"
    )

    def __repr__(self):
        return "LOBTable(" \
               "lob_type='%s', " \
               "location_id='%s', " \
               "project_id='%s'" \
               ")>" % (
                   self.lob_type,
                   self.location_id,
                   self.project_id
               )


class ProjectTable(Base):
    __tablename__ = 'project'

    project_id = Column(
        String,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("user.user_id")
    )

    created_on = Column(
        DateTime,
        default=datetime.now
    )

    country = relationship(
        "CountryTable", back_populates="project"
    )

    state = relationship(
        "StateTable", back_populates="project"
    )

    lob = relationship(
        "LOBTable", back_populates="project"
    )

    user = relationship(
        "UserTable", back_populates="project"
    )

    def __repr__(self):
        return "ProjectTable(" \
               "user_id='%s', " \
               "created_on='%s'" \
               ")>" % (
                   self.user_id,
                   self.created_on
               )


class UserTable(Base):
    __tablename__ = 'user'

    user_id = Column(
        Integer,
        primary_key=True
    )

    user_name = Column(
        String
    )

    project = relationship(
        "ProjectTable", back_populates="user"
    )

    def __repr__(self):
        return "UserTable(" \
               ")>" % (

               )
