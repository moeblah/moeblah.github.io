import os
import re
import inspect
import logging
import yaml

from os import linesep

from typing import (
    Type as _Type, List as _List, Dict as _Dict,
    Union as _Union, TypeVar as _TypeVar,
    Any as _Any, Callable as _Callable,
)


_T = _TypeVar('_T')


OWNER = '__raml_owner_class__'

ANNOTATIONS = '__annotations__'
RAML_ATTRS = '__raml_attrs__'
RAML_ATTR_NAMES = '__raml_attr_names__'
RAML_VALUE = '__raml__value__'

IS_INSTANCE = '__is_instance__'
IS_ATTR = '__is_attr__'
ATTR_NAME = '__attr_name__'
ATTR_STORE = '__attr_store__'


ORIGIN_CLASS = '__origin_class__'
ORIGIN_PROPERTIES = '__origin_properties_class__'

RAML_FILE = '__raml_file__'
EXPORT_FILE = '__export_file__'


PARENTS = '__parents__'
CHILDREN = '__children__'


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
    __export_file__: str
    __raml_attr_names__ = {}
    __parents__ = None
    __children__ = {}

    def __init__(self, *args, **kwargs):
        self.__children__ = self.__children__.copy()

        for k, v in kwargs.items():
            kwargs[k] = v or getattr(self, k, None)
        # [kwargs.update(arg) for arg in args if isinstance(arg, dict)]
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __set_name__(self, owner, name):
        owner.__children__[name] = self.__class__
        setattr(self.__class__, PARENTS, owner)
        setattr(self.__class__, ATTR_NAME, name)
        setattr(self.__class__, IS_ATTR, True)
        setattr(owner, name, self.__class__)


    @classmethod
    def __raml_dict__(cls):
        raml = {}
        attributes: list = getattr(cls, RAML_ATTRS, [])

        is_raml: _Callable[[_Any], bool] = lambda x: inspect.isclass(x) and issubclass(x, RamlMixin)

        for attr in attributes:
            value: _Union[_Type[_T], object] = getattr(cls, attr, None)
            if is_raml(value) or isinstance(value, RamlMixin):
                value = value.__raml_dict__()
            elif isinstance(value, list):
                value = [v.__raml_dict__() if is_raml(v) else v for v in value]
            if isinstance(value, (list, dict)) and len(value) == 0:
                value = None
            if value is not None:
                attr_name = cls.__raml_attr_names__.get(attr, attr)
                raml[attr_name] = value
        return raml

    @classmethod
    def __raml_yaml__(cls):
        raml = f'#%RAML 1.0{linesep}' \
               f'---{linesep}' \
               f'{yaml.dump(cls.__raml_dict__(), default_flow_style=False, allow_unicode=True)}'

        # raml = f'#%RAML 1.0{linesep}' \
        #         f'---{linesep}' \
        #         f'{yaml.dump(cls.__raml_dict__(), default_flow_style=False, allow_unicode=True, sort_keys=False)}'
        return raml


    @classmethod
    def load_raml_file(cls, filename):
        if filename:
            root_path = os.environ.get('RAML_ROOT_PATH', os.getcwd())
            file_path = filename if os.path.isabs(filename) else None
            file_path = file_path or os.path.join(root_path, filename)
            with open(os.path.abspath(file_path), 'r') as f:
                # raml = yaml.load(f, Loader=yaml.FullLoader)
                raml = yaml.load(f, Loader=yaml.Loader)
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

    @classmethod
    def export_raml(cls, filename=None):
        filename = filename or getattr(cls, EXPORT_FILE)
        raml = cls.dump_raml()
        with open(os.path.abspath(filename), 'w') as f:
            f.write(raml)

        logging.debug(f'Export raml ({cls.__name__}): {filename}')


class RamlMetaClass(type):
    def __new__(mcs, name, bases, namespace):
        if RAML_FILE in namespace:
            bases = [base.load_raml_file(filename=namespace[RAML_FILE]) for base in bases]

        attrs = list(namespace.get(RAML_ATTRS, []))
        attrs.extend(list(namespace.get(ANNOTATIONS, {})))

        for base in bases:
            if issubclass(base, RamlMixin):
                base_attributes: list = getattr(base, RAML_ATTRS, [])
                base_attributes = base_attributes.copy()
                base_attributes.extend(attrs)
                attrs = base_attributes

        attrs = list(filter(lambda x: not re.match('__.+__', x), attrs))
        namespace[RAML_ATTRS] = attrs
        namespace[IS_INSTANCE] = False
        new_class = super().__new__(mcs, name, tuple(bases), namespace)
        return new_class

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)

    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        setattr(obj, IS_INSTANCE, True)
        setattr(obj.__class__, ORIGIN_CLASS, cls)
        obj.__class__ = RamlMetaClass(f'instance.{obj.__class__.__name__}', (obj.__class__, ), obj.__dict__)
        return obj

    def __set_name__(self, owner, name):
        attr_class = RamlMetaClass(f'instance.{self.__name__}', (self, ), {})
        setattr(attr_class, PARENTS, owner)
        setattr(attr_class, ATTR_NAME, name)


class BaseRaml(RamlMixin, metaclass=RamlMetaClass):
    pass


class List(BaseRaml):
    items: _List[_Any]

    def __init__(self, *args: _Union[_Any, _List[_Any]], **kwargs):
        if len(args) > 1:
            self.items = list(args)
        elif len(args) == 1 and isinstance(args[0], list):
            self.items = args[0]
        elif len(args) == 1:
            self.items = [args[0]]
        else:
            self.items = getattr(self, 'items', [])
        super().__init__(*args, **kwargs)

    @classmethod
    def __raml_dict__(cls):
        raml = {}
        for item in cls.items:
            if inspect.isclass(item) and issubclass(item, RamlMixin):
                raml[item.__name__] = item.__raml_dict__()
        return raml or None

    @classmethod
    def load_raml(cls, raml, class_name=None):
        namespace = {'items': raml}
        return type(class_name or cls.__name__, (cls, ), namespace)


class Dict(BaseRaml):
    __items__: _Dict[str, _Any] = {}

    def __init__(self, *args, **kwargs):
        items = self.__items__.copy()

        if len(args) == 1 and isinstance(args[0], dict):
            kwargs.update(args[0])
        elif len(args) == 1 and isinstance(args[0], Dict):
            kwargs.update(args[0].__items__)
        items.update(kwargs)

        annotations = {}
        attrs = []
        for k, v in items.items():
            v = v if inspect.isclass(v) else v.__class__
            annotations[k] = _Type[v]
            attrs.append(k)

        self.__items__ = items
        setattr(self, RAML_ATTRS, attrs)
        setattr(self, ANNOTATIONS, annotations)
        super().__init__(**items)


class Properties(BaseRaml):
    __allowed__: _Union[_List[_Type[RamlMixin]], _Type[RamlMixin], None] = None
    __types__: dict = {}

    def __init__(self, *args, **kwargs):
        [kwargs.update(arg) for arg in args if isinstance(arg, dict)]
        annotations = getattr(self, ANNOTATIONS, {})
        for k, v in kwargs.items():
            annotations[k] = _Type[v] if inspect.isclass(v) else _Type[v.__class__]
        setattr(self, ANNOTATIONS, annotations)
        super().__init__(*args, **kwargs)

    def __getitem__(self, item):
        return getattr(self, item)

    @classmethod
    def __raml_dict__(cls):
        raml = super().__raml_dict__()
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
    def __raml_dict__(cls):
        items = getattr(cls, 'items', [])
        raml = tuple(items) if len(items) else None
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

    def __validate__(self, value):
        # todo : validation
        pass

    @classmethod
    def __raml_dict__(cls):
        raml = super().__raml_dict__()
        if len(raml.keys()) == 1 and 'type' in raml:
            raml = raml['type']
        return raml


Properties.__allowed__ = TypeMixin


class BaseType(TypeMixin, metaclass=RamlMetaClass):
    __annotations__ = getattr(TypeMixin, ANNOTATIONS, {})


# noinspection PyPep8Naming
class Any(BaseType):
    type = 'any'



# noinspection PyPep8Naming
class Object(BaseType):
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
            properties: Properties = None,
            minProperties: object = None,
            maxProperties: object = None,
            additionalProperties: bool = None,
            discriminator: str = None,
            discriminatorValue: str = None,
            **kwargs
    ):
        properties = properties or self.__class__.properties or Properties
        kwargs['properties'] = properties or self.__class__.properties or Properties
        kwargs['minProperties'] = minProperties
        kwargs['maxProperties'] = maxProperties
        kwargs['additionalProperties'] = additionalProperties
        kwargs['discriminator'] = discriminator
        kwargs['discriminatorValue'] = discriminatorValue
        super().__init__(*args, **kwargs)

    @classmethod
    def __raml_dict__(cls):
        if getattr(cls, IS_INSTANCE, False) and getattr(cls, ORIGIN_CLASS) is not Object:
            return cls.__name__
        else:
            raml = super().__raml_dict__()
        return raml


# noinspection PyPep8Naming
class Array(BaseType):
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
        kwargs['items'] = items or getattr(self, 'items', String)
        kwargs['minItems'] = minItems
        kwargs['maxItems'] = maxItems
        super().__init__(*args, **kwargs)


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
            for child in getattr(cls.properties, RAML_ATTRS, []):
                child = getattr(cls.properties, child, None)
                if inspect.isclass(child) and issubclass(child, Object):
                    append_item(child)
                elif isinstance(child, Object):
                    append_item(getattr(child, ORIGIN_CLASS))

        def append_item(obj):
            if isinstance(obj, Object):
                cls = getattr(obj, ORIGIN_CLASS)
            else:
                cls = obj

            if not inspect.isclass(cls) or not issubclass(cls, Object):
                return

            mro = list(cls.__mro__)
            mro.reverse()
            for base in mro:
                if not issubclass(base, Object) or base is Object:
                    continue
                if getattr(base, IS_INSTANCE, False):
                    continue
                if base in items:
                    continue
                append_children(base)
                items.append(base)

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


class QueryParameter(UriParameters):
    pass


class Body(BaseRaml):
    json: _Type[Object]
    xml: _Type[Object]

    __raml_attr_names__ = {
        'json': 'application/json',
        'xml': 'text/xml'
    }

    def __init__(self, *args, json:_Dict[str, _Any]= None, xml:_Dict[str, _Any]= None, **kwargs):
        kwargs['json'] = Object(type=None, properties=Properties(json)) if json else None
        kwargs['xml'] = Object(type=None, properties=Properties(result=xml)) if xml else None
        super().__init__(*args, **kwargs)


class Responses(Properties):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
            headers: Header = None,
            body: Body = None,
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
    responses: _Type[Responses]
    body: _Type[Body]
    protocols: _Type[Protocols]
    is_: _Type['Method']
    securedBy: str

    __raml_attr_names__ = {'is_': 'is'}

    def __init__(
            self, *args,
            displayName: str = None,
            description: str = None,
            annotations: _List[TypeMixin] = None,
            queryParameters: QueryParameter = None,
            headers: Header = None,
            queryString: Object = None,
            responses: Responses = None,
            body: Body = None,
            protocols: _List[str] = None,
            is_: Enum = None,
            securedBy: str = None,
            **kwargs
    ):
        kwargs['displayName'] = displayName
        kwargs['description'] = description
        kwargs['annotations'] = annotations
        kwargs['queryParameters'] = queryParameters or getattr(self.__class__, 'queryParameters', QueryParameter)
        kwargs['headers'] = headers or getattr(self.__class__, 'header', Header)
        kwargs['queryString'] = queryString
        kwargs['responses'] = responses
        kwargs['body'] = body
        kwargs['protocols'] = protocols or Protocols
        kwargs['is_'] = is_
        kwargs['securedBy'] = securedBy
        super().__init__(*args, **kwargs)


# noinspection PyPep8Naming
class Resource(BaseRaml):
    uri: _Union[_List[str], str]
    displayName: str
    description: str
    annotations: _List[_Type[TypeMixin]]
    is_: _Type[Enum]
    uriParameters: _Type[UriParameters]
    get: _Type[Method]
    patch: _Type[Method]
    put: _Type[Method]
    post: _Type[Method]
    delete: _Type[Method]
    options: _Type[Method]
    head: _Type[Method]
    type: _Type[TypeMixin]
    securedBy: _Any
    resources: _Type['Resources']

    __raml_attr_names__ = {'is_': 'is'}


    def __init__(
            self, *args,
            uris: _Union[_List[str], str] = None,
            displayName: str = None,
            description: str = None,
            annotations: _List[_Type[TypeMixin]] = None,
            get: Method = None,
            patch: Method = None,
            put: Method = None,
            post: Method = None,
            delete: Method = None,
            options: Method = None,
            head: Method = None,
            is_: Enum = None,
            resources: 'Resources' = None,
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
        kwargs['is_'] = is_
        kwargs['resources'] = resources
        super().__init__(*args, **kwargs)

    @classmethod
    def __raml_dict__(cls):
        raml = super().__raml_dict__()
        raml.pop('uri')
        resources: dict = raml.pop('resources', {})
        if resources:
            raml.update(resources)
        return raml


class Resources(Properties):

    def __init__(self, *args, **kwargs):
        for resource in args:
            if resource.uri in kwargs:
                continue
            kwargs[resource.uri] = resource

        for uri, resource in kwargs.items():
            if len(uri) < 2:
                raise NameError(f'Uri of {resource.__qualname__} is too short.')
            elif uri[0] != '/':
                raise NameError(f'Uri of {resource.__qualname__} should begins with slash(/).')

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


trait_attrs: list = getattr(Trait, RAML_ATTRS)
trait_attrs.insert(0, trait_attrs.pop(trait_attrs.index('usage')))


class Traits(Properties):
    pass


Traits.__allowed__ = Trait


class Api(BaseRaml):
    title: str
    description: str
    version: str
    baseUri: str
    baseUriParameters: _Type[UriParameters]
    protocols: _Type[Protocols]
    mediaType: _Type[MediaType]
    documentation: _List[_Type[Documentation]]
    uses: _Type['Uses']
    types: _Union[_Type[Types], Types]
    traits: _Type[Traits]
    resourceTypes: object
    annotations: _List[_Type[TypeMixin]]
    securitySchemes: object
    securedBy: object
    resources: _List[Resource]
    extends: str

    @classmethod
    def __raml_dict__(cls):
        raml = super().__raml_dict__()
        resources: dict = raml.pop('resources', {})
        if resources:
            raml.update(resources)
        return raml


# load from raml file
class Uses(Properties):
    # __allowed__ = [Types, 'ResourceTypes', Traits, 'SecuritySchemes', AnnotationTypes, ]
    __allowed__ = [Types, Traits, AnnotationTypes, ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # def __set_name__(self, owner, name):
    #     path = getattr(owner, RAML_FILE, None)
    #     if path is None:
    #         raise AttributeError(f'\'{RAML_FILE}\' is not specified for \'{owner}\'.')
    #     path = os.path.dirname(path)
    #
    #     for attr in getattr(self, RAML_ATTRS):
    #         filename = os.path.join(path, getattr(self, attr))
    #         if not os.path.isfile(filename):
    #             raise FileNotFoundError(f'\'{filename}\' file could not be found.')


def str_presenter(dumper, data):
    data = data.strip()
    if len(data.splitlines()) > 1:  # check for multiline string
        data = f'{os.linesep}'.join([re.sub('(^(\s{4})+)|(\s+$)', '', s) for s in data.split(os.linesep)])
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


yaml.add_representer(str, str_presenter)


def tuple_presenter(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)


yaml.add_representer(tuple, tuple_presenter)
