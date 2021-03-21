import os
import re
import inspect
import logging
import yaml

from os import linesep

from typing import (
    Type as _Type, List as _List,       # Dict as _Dict,
    Union as _Union, TypeVar as _TypeVar,
    Any as _Any, Callable as _Callable,  # Generic as _Generic,
)

# from __future__ get_annotations(import)

_T = _TypeVar('_T')


OWNER = '__raml_owner_class__'

ANNOTATIONS = '__annotations__'
ATTRS = '__raml_attrs__'
ATTR_STORE = '__raml_attr_store__'
VALUE = '__raml__value__'

IS_INSTANCE = '__is_instance__'
IS_ATTR = '__is_attr__'
ATTR_NAME = '__raml_attr_name__'

ORIGIN_CLASS = '__origin_class__'
ORIGIN_PROPERTIES = '__origin_properties_class__'

logging.basicConfig(level=logging.DEBUG)


def is_blank(obj):
    if obj is None:
        return True
    if isinstance(obj, str) and len(obj.split()) == 0:
        return True
    if isinstance(obj, (dict, list)) and len(obj) == 0:
        return True
    return False


class RamlMixin:
    def __init__(self, *args, **kwargs):
        [kwargs.update(arg) for arg in args if isinstance(arg, dict)]
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __set_name__(self, owner, name):
        namespace = self.__dict__
        origin_class = self.__class__

        namespace[ATTR_NAME] = name
        namespace[IS_INSTANCE] = True
        namespace[IS_ATTR] = True
        attr_cls = RamlMetaClass(origin_class.__name__, (origin_class, ), namespace)
        setattr(attr_cls, ORIGIN_CLASS, origin_class)
        setattr(owner, name, attr_cls)

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
            if isinstance(value, (list, dict)) and len(value) == 0:
                value = None
            if value is not None:
                raml[attr] = value
        return raml

    @classmethod
    def dump_raml(cls):
        raml = f'#%RAML 1.0{linesep}' \
                f'---{linesep}' \
                f'{yaml.dump(cls.to_raml(), default_flow_style=False, allow_unicode=True, sort_keys=False)}'
        return raml

    @classmethod
    def load_raml_file(cls, filename):
        if filename:
            root_path = os.environ.get('RAML_ROOT_PATH', os.getcwd())
            file_path = filename if os.path.isabs(filename) else None
            file_path = file_path or os.path.join(root_path, filename)
            with open(os.path.abspath(file_path), 'r') as f:
                raml = yaml.load(f, Loader=yaml.FullLoader)
        return cls.load_raml(raml=raml)

    @classmethod
    def load_raml(cls, raml, class_name=None):
        namespace = {}
        annotations = {}
        for k, v in raml.items():
            value = getattr(cls, k, v)
            if inspect.isclass(value) and issubclass(value, RamlMixin):
                value = value.load_raml(raml=v)
                annotations[k] = _Type[value]
            if type(value) == str:
                value = value.strip()
            else:
                annotations[k] = _Type[type(value)]
            namespace[k] = value
        namespace[ANNOTATIONS] = annotations
        raml_cls = type(class_name or cls.__name__, (cls, ), namespace)
        return raml_cls               # type: ignore


class RamlMetaClass(type):
    def __new__(mcs, name, bases, namespace):
        if '__raml_file__' in namespace:
            bases = [base.load_raml_file(filename=namespace['__raml_file__']) for base in bases]

        attributes: list = list(namespace.get(ANNOTATIONS, {}))
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
        if issubclass(owner, getattr(self, OWNER, type('', (object, ), {}))) and name == getattr(self, ATTR_NAME, None):
            cls = self
        else:
            namespace = dict()
            namespace[ATTR_NAME] = name
            namespace[IS_INSTANCE] = False
            namespace[IS_ATTR] = True
            cls = RamlMetaClass(self.__name__, (self, ), namespace)
            setattr(cls, ORIGIN_CLASS, self)
            setattr(cls, OWNER, owner)

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
    items: _List[_Any]

    def __init__(self, *args: _List[_Any], **kwargs):
        self.items = args if len(args) > 1 else args[0] if len(args) else getattr(self, 'items', [])
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
        setattr(self, ANNOTATIONS, kwargs)
        super().__init__(**kwargs)

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

            type_name = value.get('type', None) if isinstance(value, dict) else value
            if type_name in types:
                if isinstance(value, dict):
                    attr_cls = types[type_name].load_raml(value, class_name=attr)
                else:
                    attr_cls = type(attr, (types[type_name], ), {})
            else:
                attr_cls = None

            if inspect.isclass(attr_cls) and issubclass(attr_cls, Object):
                if attr_cls in types:
                    namespace[attr] = attr_cls()
                else:
                    namespace[attr] = attr_cls
            else:
                namespace[attr] = attr_cls

            types[attr] = attr_cls
            annotation[attr] = _Type[attr_cls]

        namespace[ANNOTATIONS] = annotation
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
    enum: _Type[Enum] = Enum
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
        kwargs['xml'] = xml or self.__class__.xml or Xml
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


class BaseType(TypeMixin, metaclass=RamlMetaClass):
    __annotations__ = getattr(TypeMixin, ANNOTATIONS, {})


# noinspection PyPep8Naming
class Any(BaseType):
    type = 'any'


class ObjectMetaClass(RamlMetaClass):
    def __new__(mcs, name, bases, namespace):

        if namespace.get(IS_INSTANCE, False):
            namespace['type'] = name = bases[0].__name__
            new_cls = super().__new__(mcs, name, bases, namespace)
            return new_cls

        if namespace.get(IS_ATTR, False):
            namespace['type'] = name = bases[0].type
            new_cls = super().__new__(mcs, name, bases, namespace)
            return new_cls

        annotations = getattr(TypeMixin, ANNOTATIONS, {})
        annotations.update(namespace.get(ANNOTATIONS, {}))
        namespace[ANNOTATIONS] = annotations

        type_name = []      # object type list
        origin_properties = namespace.pop('properties', None)
        if origin_properties is None:
            origin_properties = type('properties', (object,), {})
        elif issubclass(origin_properties, Properties):
            origin_properties_namespace = {}
            [
                origin_properties_namespace.setdefault(k, getattr(origin_properties, k))
                for k in getattr(origin_properties, ATTRS)
            ]
            origin_properties_namespace[ANNOTATIONS] = getattr(origin_properties, ANNOTATIONS, {})
            origin_properties = type('properties', (object,), origin_properties_namespace)

        properties_bases = [origin_properties, ]
        for base in bases:
            # The raml attribute value of Object is not inherited.
            [namespace.setdefault(attr, None) for attr in getattr(base, ATTRS, []) if attr not in namespace]

            try:
                if base == Object:
                    type_name.append(Object.type)
                elif not issubclass(base, RamlMetaClass):
                    type_name.append(base.__name__.split('.')[-1])
            except NameError:
                pass

            # super class of properties
            base_properties = getattr(base, ORIGIN_PROPERTIES, None)
            if base_properties is not None:
                properties_bases.append(base_properties)

        # create properties class
        properties_bases.append(Properties)
        properties_namespace = dict()
        properties_namespace[ANNOTATIONS] = getattr(origin_properties, ANNOTATIONS, {})
        properties_namespace[ATTRS] = properties_namespace[ANNOTATIONS].keys()
        properties_namespace[ATTR_NAME] = 'properties'
        properties = RamlMetaClass(f'{name}.properties', tuple(properties_bases), properties_namespace)

        if type_name:
            namespace['type'] = Enum(type_name) if len(type_name) > 1 else type_name[0]
        namespace['properties'] = properties
        namespace[ORIGIN_PROPERTIES] = origin_properties
        new_cls = super().__new__(mcs, name, bases, namespace)
        return new_cls


# noinspection PyPep8Naming
class Object(TypeMixin, metaclass=ObjectMetaClass):
    __origin_properties_class__ = None

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

    @classmethod
    def to_raml(cls):
        if getattr(cls, IS_INSTANCE, False):
            return cls.__name__
        else:
            raml = super().to_raml()
        return raml


# noinspection PyPep8Naming
class Array(BaseType, list):
    type = 'array'
    uniqueItems: bool
    items: TypeMixin
    minItems: int                           # default 0
    maxItems: int                           # default 2147483647

    def __init__(
            self, *args,
            uniqueItems: bool = None,
            items: _Any = None,
            minItems: int = None,
            maxItems: int = None,
            **kwargs
    ):
        kwargs['uniqueItems'] = uniqueItems
        kwargs['items'] = items or getattr(self.__class__, 'items', String)
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
class String(BaseType):
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
class Number(BaseType):
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


class Boolean(BaseType):
    type = 'boolean'


# noinspection PyPep8Naming
class Datetime(BaseType):
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
class File(BaseType):
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


Properties.__types__['any'] = Any
Properties.__types__['object'] = Object
Properties.__types__[''] = String
Properties.__types__[None] = Properties.__types__[''] = String
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
    items: _List[_Type[Object]]                 # type: ignore

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        items = []

        def append_children(cls):
            if not inspect.isclass(cls) or not issubclass(cls, Object):
                return
            for child in getattr(cls.properties, ATTRS, []):
                append_item(getattr(cls, child, None))

        def append_item(cls):
            if not inspect.isclass(cls) or not issubclass(cls, Object):
                return
            for base in cls.__mro__:
                if not issubclass(base, Object) or base is Object:
                    continue
                if getattr(base, IS_INSTANCE, False):
                    continue
                if base in items:
                    continue
                append_children(base)
                items.insert(0, base)

        for item in self.items:
            append_item(item)

        self.items = items


class AnnotationTypes(Properties):
    pass


class Documentation(BaseRaml):
    title: str
    content: str


class Header(Properties):
    pass


class QueryParameter(Properties):
    pass


class Body(Properties):
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
    queryParameters: _Type[QueryParameter] = QueryParameter
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
        kwargs['queryParameters'] = queryParameters or getattr(self.__class__, 'queryParameters', UriParameters)
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
    items: _List[_Type[Resource]]           # type: ignore

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
