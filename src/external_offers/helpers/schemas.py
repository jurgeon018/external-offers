from typing import Type

from cian_entities import ValueObject
from cian_schemas import EntitySchema


def get_entity_schema(entity_cls: Type[ValueObject]) -> Type[EntitySchema]:
    meta_cls = type('Meta', (), {'entity': entity_cls})
    return type(f'{entity_cls.__name__}Schema', (EntitySchema, ), {
        'Meta': meta_cls,
        '__module__': entity_cls.__module__,
    })
