# from __future__ import annotations

import os
import re
import inspect
import logging
import yaml

from os import linesep

from typing import (
    Type as _Type, List as _List,  # Dict as _Dict,
    Union as _Union, TypeVar as _TypeVar,
    Any as _Any, Callable as _Callable,  # Generic as _Generic,
)

_T = _TypeVar('_T')

ATTRS = '__raml_attrs__'
ATTR_STORE = '__raml_attr_store__'
ATTR_NAME = '__raml_attr_name__'
VALUE = '__raml__value__'


logging.basicConfig(level=logging.DEBUG)


class RamlMixin:
    def __init__(self, *args, **kwargs):
        [kwargs.update(arg) for arg in args if isinstance(arg, dict)]
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


    @classmethod
    def dump_raml(cls):
        raml =  f'#%RAML 1.0{linesep}' \
                f'---{linesep}' \
                f'{yaml.dump(cls.to_raml(), default_flow_style=False, allow_unicode=True)}'
        return raml


    @classmethod
    def load_raml_file(cls, filename):
        if filename:
            root_path  = os.environ.get('RAML_ROOT_PATH', os.getcwd())
            file_path = filename if os.path.isabs(filename) else None
            file_path = file_path or os.path.join(root_path, filename)
            with open(os.path.abspath(file_path), 'r') as f:
                raml = yaml.load(f)

        return cls.load_raml(raml=raml)

    @classmethod
    def load_raml(cls, raml, class_name = None):
        namespace = {}
        annotations = {}
        for k, v in raml.items():
            value = getattr(cls, k, v)
            if inspect.isclass(value) and issubclass(value, RamlMixin):
                value = value.load_raml(raml=v)
                annotations[k] = _Type[value]
            else:
                annotations[k] = _Type[type(value)]
            namespace[k] = value
        namespace['__annotations__'] = annotations
        raml_cls = type(class_name or cls.__name__, (cls, ), namespace)
        return raml_cls               # type: ignore



class RamlMetaClass(type):
    def __new__(mcs, name, bases, namespace):
        if '__raml_file__' in namespace:
            bases = [base.load_raml_file(filename=namespace['__raml_file__']) for base in bases]

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
        new_class = super().__new__(mcs, name, tuple(bases), namespace)
        return new_class

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
        if not inspect.isclass(attr) and hasattr(attr, '__set__'):
            attr.__set__(instance, value)

    def __get_raml_attribute__(self, instance):
        attr = self
        if instance is not None:
            attr_name = getattr(self, ATTR_NAME)
            attr_store = getattr(instance, ATTR_STORE, {})
            attr = attr_store.get(attr_name, self())
            attr_store[attr_name] = attr
            setattr(instance, ATTR_STORE, attr_store)
        return attr


class BaseRaml(RamlMixin, metaclass=RamlMetaClass):
    pass


class List(BaseRaml):
    items: _List[_Type[RamlMixin]]
    __top_classes__: _List[_Type[_T]]  = None                 # example : [RamlMixin, ]

    def __init__(self, *args: _Type[_T], **kwargs):
        items = list(getattr(self, 'items', []))

        if len(args) == 1 and not inspect.isclass(args[0]) and isinstance(args[0], list):
            items.extend(args[0])
        else:
            items.extend(args)
        self.items = []

        top_classes = [RamlMixin, BaseRaml]

        def append_item(obj):
            for base in getattr(obj, '__bases__', []):
                if top_classes is None or base in top_classes:
                    continue
                append_item(base)
            if obj not in self.items:
                self.items.append(obj)

        if self.__top_classes__ is not None:
            top_classes.extend(self.__top_classes__)
        else:
            top_classes = None

        for item in items:
            append_item(item)

        super().__init__(*args, **kwargs)

    @classmethod
    def to_raml(cls):
        raml = {}
        for item in cls.items:
            if inspect.isclass(item) and issubclass(item, RamlMixin):
                raml[item.__name__] = item.to_raml()
        return raml or None

    @classmethod
    def load_raml(cls, raml, class_name=None):
        namespace = {'items': raml}
        return type(class_name or cls.__name__, (cls, ), namespace)


def protocols_presenter(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data.items, flow_style=True)

yaml.add_representer(List, protocols_presenter)


class Properties(BaseRaml):
    __allowed__: _Union[_List[_Type[RamlMixin]], _Type[RamlMixin], None] = None
    __types__: dict = {}

    def __init__(self, *args, **kwargs):
        [kwargs.update(arg) for arg in args if isinstance(arg, dict)]
        self.__annotations__ = kwargs
        super().__init__(**kwargs)

    @classmethod
    def make(cls, **kwargs):
        annotation = kwargs.copy()
        for k, v in annotation.items():
            annotation[k] = _Type[type(v)]
        kwargs['__annotations__'] = annotation
        properties_class = RamlMetaClass('properties', (cls, ), kwargs)
        return properties_class

    def __set__(self, instance, value):
        if value is None:
            return
        if inspect.isclass(value):
            return

        assert isinstance(value, (self.__class__, dict)), \
            f'({instance}, {value}) Value for {self.__class__} must be instance of {self.__class__} or dict.'

        value = value if isinstance(value, dict) else getattr(value, ATTR_STORE, {})
        attrs: dict = getattr(self, ATTR_STORE, {})
        attrs.update(value)
        setattr(self, ATTR_STORE, attrs)

    @classmethod
    def to_raml(cls):
        raml = super().to_raml()
        return raml if len(raml) else None

    @classmethod
    def load_raml(cls, raml):
        attrs = list(raml.keys())
        types = cls.__types__.copy()

        namespace = {}
        annotation = {}
        while len(attrs):
            attr = attrs.pop(0)
            value = raml.get(attr)

            type_ =  value.get('type', None) if isinstance(value, dict) else value
            if type_ in types:
                if isinstance(value, dict):
                    attr_cls = types[type_].load_raml(value, class_name=attr)
                else:
                    attr_cls = type(attr, (types[type_], ), {})
            else:
                attr_cls = None

            types[attr] = attr_cls
            namespace[attr] = attr_cls
            annotation[attr] = _Type[attr_cls]

        namespace['__annotations__'] = annotation
        raml_cls = type(cls.__name__, (cls, ), namespace)
        raml_cls.__types__ = types
        return raml_cls


class UriParameters(Properties):
    pass



class Enum(List):
    @classmethod
    def to_raml(cls):
        items = getattr(cls, 'items', [])
        raml = List(items) if len(items) else None
        return raml


class Protocols(Enum):
    http = 'HTTP'
    https = 'HTTPS'


class MediaType(Enum):
    json = 'application/json'
    xml = 'application/xml'


class Xml(BaseRaml):
    attribute: bool  # default false
    wrapped: bool  # default false
    name: str
    namespace: str
    prefix: str


class Facets(Properties):
    pass


# noinspection PyPep8Naming
class TypeMixin(RamlMixin):
    annotations: _List[_Type['TypeMixin']]
    type: str
    displayName: str
    description: str
    enum: _List[object] = Enum
    facets: _Type[Facets] = Facets
    default: object
    example: object
    examples: object
    xml: _Type[Xml] = Xml

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
        kwargs['enum'] = enum or self.__class__.enum or Enum
        kwargs['facets'] = facets or self.__class__.facets or Facets
        kwargs['default'] = default
        kwargs['example'] = example
        kwargs['examples'] = examples
        kwargs['xml'] = xml or self.__class__.facets or Facets
        super().__init__(*args, **kwargs)

    def __get__(self, instance, owner):
        value = getattr(self, VALUE, None)
        return value

    def __set__(self, instance, value):
        setattr(self, VALUE, value)

    @classmethod
    def __validate__(cls, value):
        # todo : validation
        pass

    @classmethod
    def to_raml(cls):
        raml = super().to_raml()
        if len(raml.keys()) == 1 and 'type' in raml:
            raml = raml['type']
        return raml





Properties.__allowed__ = TypeMixin


class Type(TypeMixin, metaclass=RamlMetaClass):
    __annotations__ = dict(TypeMixin.__annotations__)


# noinspection PyPep8Naming
class Any(Type, metaclass=RamlMetaClass):
    pass


class ObjectMetaClass(RamlMetaClass):
    def __new__(mcs, name, bases, namespace):
        annotations = dict(TypeMixin.__annotations__)
        annotations.update(namespace.get('__annotations__', {}))
        namespace['__annotations__'] = annotations

        type_ = []      # object type list

        # inherit properties
        base_properties_attrs = []
        properties = namespace.get('properties', type('properties', (Properties, ), {}))
        properties_annotations = getattr(properties, '__annotations__')

        for base in bases:
            try:
                type_.append(base.type if base == Object else base.__name__)
            except NameError:
                continue

            base_properties = getattr(base, 'properties', None)
            if base_properties is None:
                continue

            base_attrs = getattr(base_properties, ATTRS, [])
            for base_attr in base_attrs:
                if hasattr(properties, base_attr):
                    continue
                setattr(properties, base_attr, getattr(base_properties, base_attr))

            base_properties_attrs.extend(getattr(base_properties, ATTRS, []))

        properties_namespace = {'__annotations__': properties_annotations}
        properties = RamlMetaClass(properties.__qualname__, (properties, ), properties_namespace)
        # properties_attrs = getattr(properties, ATTRS, [])
        # # properties_attrs = list(filter(lambda x: x not in base_properties_attrs, properties_attrs))
        # setattr(properties, ATTRS, properties_attrs)
        setattr(properties, ATTR_NAME, 'properties')
        namespace['properties'] = properties
        new_cls = super().__new__(mcs, name, bases, namespace)

        # remove base attribute value
        for base in bases:
            for attr in getattr(base, ATTRS, []):
                if attr in namespace:
                    continue
                else:
                    setattr(new_cls, attr, None)

        if type_:
            new_cls.type = type_ if len(type_) > 1 else type_[0]

        return new_cls


    def __set_name__(self, owner, name):
        return self


# noinspection PyPep8Naming
class Object(TypeMixin, metaclass=ObjectMetaClass):
    type = 'object'
    properties: _Type[Properties] = Properties
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
        kwargs['properties'] = properties or self.__class__.properties or Properties
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
        assert isinstance(value, (self.__class__, self.properties.__class__, dict)) or value is None, \
            f'Value for {self} must be instance of {self.__class__}, {self.properties.__class__} or dict. ' \
            f'({instance}, {value})'

        if isinstance(value, self.__class__):
            value = value.properties

        # todo : if the value is instance of dict or None

        setattr(self, 'properties', value)


# noinspection PyPep8Naming
class Array(Any, list):
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

    def __get__(self, instance, owner):
        return self

    def __set__(self, instance, value):
        pass

    def __str__(self):
        return f'{self.__class__.__name__}{super().__str__()}'

    def append(self, __object: _T) -> None:
        super().append(__object)

    def insert(self, __index: int, __object: _T) -> None:
        super().insert(__index, __object)


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


Properties.__types__[None] = Properties.__types__[''] = Any
Properties.__types__['object'] = Object
Properties.__types__['string'] = String
Properties.__types__['number'] = Number
Properties.__types__['integer'] = Number
Properties.__types__['boolean'] = Boolean
Properties.__types__['date-only'] = DateOnly
Properties.__types__['time-only'] = TimeOnly
Properties.__types__['datetime-only'] = DatetimeOnly
Properties.__types__['datetime'] = Datetime
Properties.__types__['file'] = File


class Types(List):
    items: _List[_Type[Type]]
    __top_classes__ = [Object, ]


class AnnotationTypes(Properties):
    pass


class Documentation(BaseRaml):
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
    headers: _Type[Header] = Header
    queryString: _Type[Object]  # The queryString and queryParameters nodes are mutually exclusive.
    response: _Type[Response]
    body: _Type[Body]
    protocols: _Type[Protocols]
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
        kwargs['headers'] = headers or getattr(self.__class__, 'header', Header)
        kwargs['queryString'] = queryString
        kwargs['response'] = response
        kwargs['body'] = body
        kwargs['protocols'] = protocols or Protocols
        kwargs['is'] = is_
        kwargs['securedBy'] = securedBy
        super().__init__(*args, **kwargs)


# noinspection PyPep8Naming
class Resource(BaseRaml):
    uri: _Union[_List[str], str]
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
    is_: _Type['Method']
    '''type: _Type[ResourceType]'''
    # securedBy:
    uriParameters: _Type[UriParameters]
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


class Resources(List):
    items: _List[_Type[Resource]]
    __top_classes__ = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uris = {}
        for resource in self.items:
            # check uri
            if resource.uri in uris:
                already_resource = uris[resource.uri]
                raise KeyError(
                    f'\'{resource.uri}\' of {resource.__qualname__} '
                    f'is already been used at {already_resource.__qualname__}'
                )
            elif len(resource.uri) < 2:
                raise NameError(f'Uri of {resource.__qualname__} is too short.')
            elif resource.uri[0] != '/':
                raise NameError(f'Uri of {resource.__qualname__} should begins with slash(/).')
            else:
                uris[resource.uri] = resource

        self.__uris__ = uris


    @classmethod
    def to_raml(cls):
        raml = super().to_raml()
        for k in list(raml.keys()):
            resource = raml.pop(k)
            uri = resource.pop('uri')
            raml[uri] = resource
        return raml


class Trait(Method):
    usage: str

    def __init__(
            self, *args,
            usage: str = None,
            **kwargs
    ):
        kwargs['usage'] = usage
        super().__init__(*args, **kwargs)

trait_attrs: list = getattr(Trait, ATTRS)
trait_attrs.insert(0, trait_attrs.pop(trait_attrs.index('usage')))

class Traits(Properties):
    pass


Traits.__allowed__ = Trait


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
    protocols: _Type[Protocols]
    mediaType: _Type[MediaType]
    documentation: _List[_Type[Documentation]]
    types: _Union[_Type[Types], Types]
    traits: _Type[Traits]
    resourceTypes: object
    annotations: _List[_Type[TypeMixin]]
    securitySchemes: object
    securedBy: object
    uses: _Type[Uses]
    resources: _List[Resource]
    extends: str

    @classmethod
    def to_raml(cls):
        raml = super().to_raml()
        resources: dict = raml.pop('resources', {})
        if resources:
            raml.update(resources)
        return raml



def str_presenter(dumper, data):
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)

def tuple_presenter(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', list(data), flow_style=True)

yaml.add_representer(tuple, tuple_presenter)
