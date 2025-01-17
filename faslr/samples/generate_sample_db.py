# Generates the example database (used for tutorials, testing)

import os
import faslr.utilities # noqa
import pandas as pd
import sqlalchemy as sa

from faslr import schema
from faslr.utilities.queries import delete_country

from faslr.schema import (
    UserTable,
    CountryTable,
    LocationTable,
    StateTable,
    LOBTable,
    ProjectTable,
    ProjectViewTable,
    ProjectViewData
)

from sqlalchemy.orm import sessionmaker
from uuid import uuid4

db_name = 'sample.db'

try:
    os.remove(db_name)
except OSError:
    pass

engine = sa.create_engine(
    'sqlite:///' + db_name,
    echo=True,
    connect_args={
        'check_same_thread': False
    }
)


schema.Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()
connection = engine.connect()

country_uuid = str(uuid4())
state_uuid = str(uuid4())
lob_uuid = str(uuid4())

new_country_project = ProjectTable(project_id=country_uuid)
new_state_project = ProjectTable(project_id=state_uuid)
new_lob_project = ProjectTable(project_id=lob_uuid)

new_country_location = LocationTable(hierarchy="country")
new_state_location = LocationTable(hierarchy="state")

session.add(new_country_project)
session.add(new_country_location)
session.add(new_lob_project)
session.add(new_state_project)
session.add(new_state_location)
session.flush()

new_country = CountryTable(
    location_id=new_country_location.location_id,
    country_name="USA",
    project_id=new_country_project.project_id
)

session.add(new_country)
session.flush()

new_state = StateTable(
    location_id=new_state_location.location_id,
    state_name="Texas",
    country_id=new_country.country_id,
    project_id=new_state_project.project_id
)

new_lob = LOBTable(
    lob_type="Auto",
    location_id=new_state_location.location_id,
    project_id=new_lob_project.project_id
)

path = os.path.dirname(os.path.abspath(__file__))
df_steady_state = pd.read_csv(os.path.join(path, "friedland_us_auto_steady_state.csv"))

project_view = ProjectViewTable(
    name="Auto",
    description="Auto Steady State",
    origin="Accident Year",
    development="Calendar Year",
    columns="Paid Claims;Reported Claims",
    cumulative=True,
    project_id=new_lob_project.project_id
)

session.add(new_state)
session.add(new_lob)
session.add(project_view)
session.flush()

df_steady_state.columns = [
            'accident_year',
            'calendar_year',
            'paid_loss',
            'reported_loss'
]

df_steady_state['view_id'] = project_view.view_id

data_list = df_steady_state.to_dict('records')

obj_list = []
for record in data_list:
    data_obj = ProjectViewData(**record)
    obj_list.append(data_obj)

session.add_all(obj_list)

session.commit()
session.close()
