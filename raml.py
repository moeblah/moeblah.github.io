# from __future__ import annotations

import re
import inspect
import logging

from typing import (
    Type as _Type, List as _List,  # Dict as _Dict,
    Union as _Union, TypeVar as _TypeVar,
    Generic as _Generic, Any as _Any, Callable as _Callable,
)

_T = _TypeVar('_T')

ATTRS = '__raml_attrs__'
ATTR_STORE = '__raml_attr_store__'
ATTR_NAME= '__raml_attr_name__'
VALUE = '__raml__value__'


logging.basicConfig(level=logging.DEBUG)


class RamlMixin:
    def __init__(self, *args, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __set_name__(self, owner, name):
        cls = RamlMetaClass(name, (self.__class__, ), self.__dict__)
        setattr(cls, ATTR_NAME, name)
        setattr(owner, name, cls)

    def __get__(self, instance, owner):
        return self

    def __set__(self, instance, value):
        pass


    @classmethod
    def to_raml(cls):
        raml = {}
        attributes: list = getattr(cls, ATTRS, [])

        is_raml: _Callable[[_Any], bool] = lambda x: inspect.isclass(x) and issubclass(x, RamlMixin)

        for attr in attributes:
            value: _Union[_Type[_T], object] = getattr(cls, attr, None)
            if is_raml(value):
                value = value.to_raml()
            elif isinstance(value, list):
                value = [v.to_raml() if is_raml(v) else v for v in value]
            if value is not None:
                raml[attr] = value
        return raml


class RamlMetaClass(type):
    def __new__(mcs, name, bases, namespace):
        attributes: list = list(namespace.get('__annotations__', {}))
        attributes = attributes.copy()
        for base in bases:
            if issubclass(base, RamlMixin):
                base_attributes: list = getattr(base, ATTRS, [])
                base_attributes = base_attributes.copy()
                base_attributes.extend(attributes)
                attributes = base_attributes

        attributes = list(filter(lambda x: not re.match('__.+__', x), attributes))
        namespace[ATTRS] = attributes
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)

    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        return obj

    def __set_name__(self, owner, name):
        cls = RamlMetaClass(name, (self, ), {})
        setattr(cls, ATTR_NAME, name)
        setattr(owner, name, cls)

    def __get__(self, instance, owner):
        attr = self.__get_raml_attribute__(instance)
        if not inspect.isclass(attr) and hasattr(attr, '__get__'):
            attr = attr.__get__(instance, owner)
        return attr

    def __set__(self, instance, value):
        attr = self.__get_raml_attribute__(instance)
        if hasattr(attr, '__set__'):
            attr.__set__(instance, value)

    def __get_raml_attribute__(self, instance):
        attr = self
        if instance :
            attr_name = getattr(self, ATTR_NAME)
            attr_store = getattr(instance, ATTR_STORE, {})
            attr = attr_store.get(attr_name, self())
            attr_store[attr_name] = attr
            setattr(instance, ATTR_STORE, attr_store)
        return attr



class BaseRaml(RamlMixin, metaclass=RamlMetaClass):
    pass


class RamlList(BaseRaml):
    __items__: _List[BaseRaml]

    def append(self, obj: BaseRaml):
        self.__items__.append(obj)

    def insert(self, index: int, obj: BaseRaml):
        self.__items__.insert(index, obj)

    def items(self) -> list:
        return self.__items__


class Xml(BaseRaml):
    attribute: bool  # default false
    wrapped: bool  # default false
    name: str
    namespace: str
    prefix: str


class Properties(BaseRaml):
    __allowed__: _Union[_List[_Type[BaseRaml]], _Type[BaseRaml], None] = None

    def __init__(self, *args, **kwargs):
        self.__annotations__ = kwargs
        super().__init__(*args, **kwargs)

    @classmethod
    def make(cls, **kwargs):
        annotation = kwargs.copy()
        for k, v in annotation.items():
            annotation[k] = _Type[type(v)]
        kwargs['__annotations__'] = annotation
        properties_class = RamlMetaClass('properties', (cls, ), kwargs)
        return properties_class

    def __set__(self, instance, value):
        if value is None: return
        if inspect.isclass(value): return

        assert isinstance(value, (self.__class__, dict)), \
            f'({instance}, {value}) Value for {self.__class__} must be instance of {self.__class__} or dict.'

        value = value if isinstance(value, dict) else getattr(value, ATTR_STORE, {})
        attrs:dict = getattr(self, ATTR_STORE, {})
        attrs.update(value)
        setattr(self, ATTR_STORE, attrs)

    @classmethod
    def to_raml(cls):
        raml = super().to_raml()
        return raml if len(raml) else None

class Facets(Properties):
    pass


class AnnotationTypes(Properties):
    pass


class Types(Properties):
        pass


# noinspection PyPep8Naming
class TypeMixin(RamlMixin):
    annotations: _List[_Type['TypeMixin']]
    type: str
    displayName: str
    description: str
    enum: _List[object]
    facets: _Type[Facets]
    default: object
    example: object
    examples: object
    xml: _Type[Xml]

    def __init__(
            self, *args,
            type_: str = None,
            annotations: _List[_Type['TypeMixin']] = None,
            displayName: str = None,
            description: str = None,
            enum: _List[object] = None,
            facets: _Type[Facets] = None,
            default: object = None,
            example: object = None,
            examples: object = None,
            xml: _Type[Xml] = None,
            **kwargs
    ):

        kwargs['type'] = getattr(self.__class__, 'type',  type_)
        kwargs['annotations'] = annotations
        kwargs['displayName'] = displayName
        kwargs['description'] = description
        kwargs['enum'] = enum
        kwargs['facets'] = facets
        kwargs['default'] = default
        kwargs['example'] = example
        kwargs['examples'] = examples
        kwargs['xml'] = xml
        super().__init__(*args, **kwargs)


    def __get__(self, instance, owner):
        value = getattr(self, VALUE, None)
        return value

    def __set__(self, instance, value):
        setattr(self, VALUE, value)


TypeMixin = RamlMetaClass('TypeMixin', (TypeMixin, ), {'__annotations__': TypeMixin.__annotations__})
Properties.__allowed__ = TypeMixin


# noinspection PyPep8Naming
class Any(TypeMixin, metaclass=RamlMetaClass):
    pass


class ObjectMetaClass(RamlMetaClass):
    def __new__(mcs, name, bases, namespace):
        type_ = []
        base_properties_attrs = []
        properties = namespace.get('properties', Properties)
        properties_bases = [properties, ]
        for base in bases:
            try:
                type_.append(base.type if base == Object else base.__name__)
            except NameError:
                pass

            base_properties = getattr(base, 'properties', None)
            if base_properties is None or base_properties in properties_bases: continue
            properties_bases.insert(0, base_properties)
            base_properties_attrs.extend(getattr(base_properties, ATTRS, []))

        properties_annotations = getattr(properties, '__annotations__')
        properties_namespace = {'__annotations__': properties_annotations}
        properties = RamlMetaClass(properties.__qualname__, tuple(properties_bases), properties_namespace)
        properties_attrs = getattr(properties, ATTRS, [])
        properties_attrs = list(filter(lambda x: x not in base_properties_attrs, properties_attrs))
        setattr(properties, ATTRS, properties_attrs)

        if type_: namespace['type'] = type_ if len(type_) > 1 else  type_[0]
        namespace['properties'] = properties
        return super().__new__(mcs, name, bases, namespace)


# noinspection PyPep8Naming
class Object(TypeMixin, metaclass=ObjectMetaClass):

    type = 'object'
    properties: _Type[Properties]
    minProperties: object
    maxProperties: object
    additionalProperties: bool  # default true
    discriminator: str
    discriminatorValue: str  # default The name of type

    def __init__(
            self,
            *args,
            properties: _Type[Properties] = None,
            minProperties: object = None,
            maxProperties: object = None,
            additionalProperties: bool = None,
            discriminator: str = None,
            discriminatorValue: str = None,
            **kwargs
    ):
        kwargs['properties'] = properties
        kwargs['minProperties'] = minProperties
        kwargs['maxProperties'] = maxProperties
        kwargs['additionalProperties'] = additionalProperties
        kwargs['discriminator'] = discriminator
        kwargs['discriminatorValue'] = discriminatorValue
        super().__init__(*args, **kwargs)

    def __get__(self, instance, owner):
        value = getattr(self, 'properties', None)
        return value

    def __set__(self, instance, value):
        assert isinstance(value, (self.__class__, self.properties.__class__, dict)), \
            f'Value for {self} must be instance of {self.__class__}, {self.properties.__class__} or dict.'

        if isinstance(value, self.__class__):
            value = value.properties

        setattr(self, 'properties', value)


# noinspection PyPep8Naming
class Array(Any):
    type = 'array'
    uniqueItems: bool
    items: _Type[TypeMixin]
    minItems: int                           # default 0
    maxItems: int                           # default 2147483647

    def __init__(
            self, *args,
            uniqueItems: bool = None,
            items: _Type[TypeMixin] = None,
            minItems: int = None,
            maxItems: int = None,
            **kwargs
    ):
        kwargs['uniqueItems'] = uniqueItems
        kwargs['items'] = items
        kwargs['minItems'] = minItems
        kwargs['maxItems'] = maxItems
        super().__init__(*args, **kwargs)


# noinspection PyPep8Naming
class String(Any):
    type = 'string'
    minLength: int  # default 0
    maxLength: int  # default 2147483647
    pattern: str  # Regular expression

    def __init__(
            self, *args,
            minLength: int = None,
            maxLength: int = None,
            pattern: str = None,
            **kwargs
    ):
        kwargs['minLength'] = minLength
        kwargs['maxLength'] = maxLength
        kwargs['pattern'] = pattern
        super().__init__(*args, **kwargs)


# noinspection PyPep8Naming
class Number(Any):
    type = 'number'
    minimum: int
    maximum: int
    format: str
    multipleOf: int

    def __init__(
            self, *args,
            minimum: int = None,
            maximum: int = None,
            format_: str = None,
            multipleOf: int = None,
            **kwargs
    ):
        kwargs['minimum'] = minimum
        kwargs['maximum'] = maximum
        kwargs['format'] = format_
        kwargs['multipleOf'] = multipleOf
        super().__init__(*args, **kwargs)


class Int(Number):
    format = 'int'


class Int8(Number):
    format = 'int8'


class Int16(Number):
    format = 'int16'


class Int32(Number):
    format = 'int16'


class Int64(Number):
    format = 'int16'


class Float(Number):
    format = 'float'


class Long(Number):
    format = 'Long'


class Double(Number):
    format = 'Double'


class Integer(Int8):
    type = 'integer'


class Boolean(Any):
    type = 'boolean'


# noinspection PyPep8Naming
class Datetime(Any):
    type = 'datetime'
    format: str  # default RFC3339 yyyy-mm-ddThh: mm: ss[.ff...]Z

    def __init__(
            self, *args,
            format_: str = None,
            **kwargs
    ):
        kwargs['format'] = format_
        super().__init__(*args, **kwargs)


class DatetimeOnly(Datetime):
    type = 'datetime-only'  # default RFC3339 yyyy-mm-ddThh: mm: ss[.ff...]


class DateOnly(Datetime):
    type = 'date-only'  # default RFC3339 yyyy-mm-dd


class TimeOnly(Datetime):
    type = 'time-only'  # default RFC3339 hh: mm: ss[.ff...]


# noinspection PyPep8Naming
class File(Any):
    type = 'file'
    fileTypes: _List[str]
    minLength: int  # default = 0
    maxLength: int  # default = 2147483647

    def __init__(
            self, *args,
            fileTypes: _List[str] = None,
            minLength: int = None,
            maxLength: int = None,
            **kwargs
    ):
        kwargs['fileTypes'] = fileTypes
        kwargs['minLength'] = minLength
        kwargs['maxLength'] = maxLength
        super().__init__(*args, **kwargs)


class UriParameters(Properties):
    pass


class DocumentationItem(BaseRaml):
    title: str
    content: str


class Header(Properties):
    pass


class QueryParameter(Properties):
    pass


class Body(Object):
    pass


# noinspection PyPep8Naming
class Response(BaseRaml):
    description: str
    annotations: _List[_Type[TypeMixin]]
    headers: _Type[Header]
    body: _Type[Body]

    def __init__(
            self, *args,
            description: str = None,
            annotations: _List[_Type[TypeMixin]] = None,
            headers: _Type[Header] = None,
            body: _Type[Body] = None,
            **kwargs
    ):
        kwargs['description'] = description
        kwargs['annotations'] = annotations
        kwargs['headers'] = headers
        kwargs['body'] = body
        super().__init__(*args, **kwargs)


# noinspection PyPep8Naming
class Method(BaseRaml):
    displayName: str
    description: str
    annotations: _List[_Type[TypeMixin]]
    queryParameters: _Type[QueryParameter]
    headers: _Type[Header]
    queryString: _Type[Object]  # The queryString and queryParameters nodes are mutually exclusive.
    response: _Type[Response]
    body: _Type[Body]
    protocols: _List[str]
    is_: _Type['Method']
    securedBy: str

    def __init__(
            self, *args,
            displayName: str = None,
            description: str = None,
            annotations: _List[_Type[TypeMixin]] = None,
            queryParameters: _Type[QueryParameter] = None,
            headers: _Type[Header] = None,
            queryString: _Type[Object] = None,
            response: _Type[Response] = None,
            body: _Type[Body] = None,
            protocols: _List[str] = None,
            is_: _Type['Method'] = None,
            securedBy: str = None,
            **kwargs
    ):
        kwargs['displayName'] = displayName
        kwargs['description'] = description
        kwargs['annotations'] = annotations
        kwargs['queryParameters'] = queryParameters
        kwargs['headers'] = headers
        kwargs['queryString'] = queryString
        kwargs['response'] = response
        kwargs['body'] = body
        kwargs['protocols'] = protocols
        kwargs['is'] = is_
        kwargs['securedBy'] = securedBy
        super().__init__(*args, **kwargs)


class Trait(Method):
    usage: str

    def __init__(
            self, *args,
            usage: str = None,
            **kwargs
    ):
        kwargs['usage'] = usage
        super().__init__(*args, **kwargs)


class Traits(Properties):
    pass


Traits.__allowed__ = Trait


# noinspection PyPep8Naming
class Resource(BaseRaml):
    uris: _Union[_List[str], str]
    displayName: str
    description: str
    annotations: _List[_Type[TypeMixin]]
    get: _Type[Method]
    patch: _Type[Method]
    put: _Type[Method]
    post: _Type[Method]
    delete: _Type[Method]
    options: _Type[Method]
    head: _Type[Method]
    resources: _List[_Type['Resource']]

    def __init__(
            self, *args,
            uris: _Union[_List[str], str] = None,
            displayName: str = None,
            description: str = None,
            annotations: _List[_Type[TypeMixin]] = None,
            get: _Type[Method] = None,
            patch: _Type[Method] = None,
            put: _Type[Method] = None,
            post: _Type[Method] = None,
            delete: _Type[Method] = None,
            options: _Type[Method] = None,
            head: _Type[Method] = None,
            resources: _List[_Type['Resource']] = None,
            **kwargs
    ):
        kwargs['uris'] = uris
        kwargs['displayName'] = displayName
        kwargs['description'] = description
        kwargs['annotations'] = annotations
        kwargs['get'] = get
        kwargs['patch'] = patch
        kwargs['put'] = put
        kwargs['post'] = post
        kwargs['delete'] = delete
        kwargs['options'] = options
        kwargs['head'] = head
        kwargs['resources'] = resources
        super().__init__(*args, **kwargs)


# load from raml file
class Uses(Properties):
    # __allowed__ = [Types, 'ResourceTypes', Traits, 'SecuritySchemes', AnnotationTypes, ]
    __allowed__ = [Types, Traits, AnnotationTypes, ]


class Api(BaseRaml):
    title: str
    description: str
    version: str
    baseUri: str
    baseUriParameters: _Type[UriParameters]
    protocols: _List[str]
    mediaType: _Union[_List[str], str]
    documentation: _List[_Type[DocumentationItem]]
    types: _Type[Types]
    traits: _Type[Traits]
    resourceTypes: object
    annotations: _List[_Type[TypeMixin]]
    securitySchemes: object
    securedBy: object
    uses: _Type[Uses]
    resources: _List[Resource]
    extends: str                                # raml file name todo:
