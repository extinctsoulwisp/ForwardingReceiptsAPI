import datetime
from typing import Annotated

from sqlalchemy import func, SMALLINT, DATE
from sqlalchemy.orm import mapped_column

int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime.datetime, mapped_column(server_default=func.now(), onupdate=datetime.datetime.now)]

str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]
str_null_false = Annotated[str, mapped_column(nullable=True)]

smallint_null_true = Annotated[int, mapped_column(SMALLINT, nullable=True)]
smallint_null_false = Annotated[int, mapped_column(SMALLINT, nullable=False)]

float_null_false = Annotated[float, mapped_column(nullable=False)]

bool_null_false = Annotated[bool, mapped_column(nullable=False)]

date_null_true = Annotated[datetime.date, mapped_column(DATE, nullable=True)]
