from .organization import OrganizationRead
from .drug import DrugRead, DrugListItem

OrganizationRead.model_rebuild()
DrugRead.model_rebuild()
DrugListItem.model_rebuild()