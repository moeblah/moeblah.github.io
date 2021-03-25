import os
import re
import inspect
import logging
import yaml

from os import linesep

from typing import (
    Type as _Type, List as _List, Dict as _Dict,
    Union as _Union, TypeVar as _TypeVar,
    Any as _Any
)


_T = _TypeVar('_T')


OWNER = '__raml_owner_class__'

ANNOTATIONS = '__annotations__'
RAML_ATTRS = '__raml_attrs__'
RAML_ATTR_NAMES = '__raml_attr_names__'
RAML_VALUE = '__raml__value__'


IS_INSTANCE = '__is_instance__'
IS_ATTR = '__is_attr__'
IS_SINGLE_OBJECT = '__is_single_object__'
IS_DYNAMIC_OBJECT= '__is_dynamic_object__'
ATTR_NAME = '__attr_name__'
ATTR_STORE = '__attr_store__'


ORIGIN_CLASS = '__origin_class__'
ORIGIN_PROPERTIES = '__origin_properties_class__'

RAML_FILE = '__raml_filename__'
EXPORT_FILE = '__export_filename__'


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
    __raml_attr_names__: _Dict[str, str] = {}
    __parents__ = None
    __children__: _Dict[str, _Type['RamlMixin']] = {}

    def __init__(self, *args, **kwargs):
        self.__children__ = self.__children__.copy()

        for k, v in kwargs.items():
            kwargs[k] = v if v is not None else getattr(self, k, None)
        for key, item in kwargs.items():
            setattr(self, key, item)

    def __set_name__(self, owner, name):
        owner_children = getattr(owner, CHILDREN, {})
        owner_children[name] = self.__class__
        setattr(owner, CHILDREN, owner_children)
        setattr(self.__class__, PARENTS, owner)
        setattr(self.__class__, ATTR_NAME, name)
        setattr(self.__class__, IS_ATTR, True)
        setattr(owner, name, self.__class__)

    @classmethod
    def __get_parent_filepath__(cls):
        parent = getattr(cls, PARENTS, None)
        if parent is None:
            return ''

        filepath = getattr(parent, RAML_FILE, None)
        if filepath is None:
            filepath = parent.__get_parent_filepath__()

        filepath = cls.__get_abspath__(os.path.dirname(filepath))
        return filepath

    @classmethod
    def __get_abspath__(cls, filepath, root_path=None):
        root_path = root_path if root_path else os.environ.get('RAML_ROOT_PATH', os.getcwd())
        if os.path.isfile(root_path):
            root_path = os.path.dirname(root_path)
        abspath = filepath if os.path.isabs(filepath) else None
        abspath = abspath or os.path.join(root_path, filepath)
        abspath = os.path.abspath(abspath)
        print(abspath)
        return abspath

    @classmethod
    def __get_attr_type__(cls, attr):
        attr_type = None
        for mro in cls.__mro__:
            attr_type = getattr(mro, ANNOTATIONS, {}).get(attr, None)
            if attr_type is not None:
                break
        return attr_type

    @classmethod
    def __is_raml__(cls, value):
        is_raml = not (
                not (inspect.isclass(value) and issubclass(value, RamlMixin)) and not isinstance(value, RamlMixin)
        )
        return is_raml

    @classmethod
    def __raml_dict__(cls):
        raml = {}
        attrs: list = getattr(cls, RAML_ATTRS, [])

        for attr in attrs:
            value: _Union[_Type[_T], object] = getattr(cls, attr, None)

            if cls.__is_raml__(value):
                if getattr(value, RAML_FILE, None):
                    parent_filepath = cls.__get_parent_filepath__()
                    raml_file = cls.__get_abspath__(getattr(value, RAML_FILE))
                    value = f'!include {os.path.relpath(raml_file, parent_filepath)}'
                else:
                    value = value.__raml_dict__()
            elif isinstance(value, list):
                value = [v.__raml_dict__() if cls.__is_raml__(v) else v for v in value]
            elif isinstance(value, dict):
                for k, v in value.items():
                    value[k] = v.__raml_dict__() if cls.__is_raml__(v) else v
            if isinstance(value, (list, dict)) and len(value) == 0:
                value = None
            if value is not None:
                attr_name =  getattr(cls, RAML_ATTR_NAMES, {}).get(attr, attr)
                raml[attr_name] = value
        return raml

    @classmethod
    def __dump_raml__(cls):
        raml_dict = cls.__raml_dict__()
        raml = f'{yaml.dump(raml_dict, default_flow_style=False, allow_unicode=True)}'

        # raml_dict = cls.__raml_dict__()
        # raml = f'#%RAML 1.0{linesep}' \
        #        f'---{linesep}' \
        #        f'{yaml.dump(raml_dict, default_flow_style=False, allow_unicode=True, sort_keys=False)}'
        raml = re.sub(r"'(!include .+)'", r"\g<1>", raml)
        return raml

    @classmethod
    def __export_raml__(cls, filename=None):
        filename = filename or getattr(cls, EXPORT_FILE)
        raml = cls.__dump_raml__()
        with open(os.path.abspath(filename), 'w') as f:
            f.write(raml)
        logging.debug(f'Export raml ({cls.__name__}): {filename}')

    @classmethod
    def __import_raml__(cls, filename=None):
        filename = filename or getattr(cls, RAML_FILE)
        if filename:
            filepath = cls.__get_abspath__(filename)

            with open(filepath, 'r') as f:
                yaml_string = f.read()
            #yaml.load(yaml_string, Loader=yaml.FullLoader)
            yaml_string = re.sub(r"(!include\s+.+)", r"'\g<1>'", yaml_string)
            raml = yaml.load(yaml_string)

            new_cls = cls.__load_raml__(raml, filepath=filepath)

            setattr(new_cls, RAML_FILE, filepath)
            return new_cls
        return cls

    @classmethod
    def __raml_loader__(cls, raml, class_name=None, **kwargs):
        namespace = {}
        annotations = {}

        for k, v in raml.items():
            value_type = cls.__get_attr_type__(k)

            if  inspect.isclass(value_type) and issubclass(value_type, RamlMixin):
                value = value_type.__load_raml__(v, class_name=class_name, **kwargs)
            else:
                value = v
                if type(value) is str:
                    value = value.strip()
            annotations[k] = value_type
            namespace[k] = value

        namespace[ANNOTATIONS] = annotations
        raml_cls = type(class_name or cls.__name__, (cls, ), namespace)
        return raml_cls               # type: ignore


    @classmethod
    def __load_raml__(cls, raml, class_name=None, filepath=None):
        value = raml
        if isinstance(raml, str):
            if re.match('!include\s+.+', raml):
                filename = re.match('!include\s+(.+)', raml)[1]
                filename = cls.__get_abspath__(filename, root_path=filepath)
                new_cls =cls.__import_raml__(filename)
                value = new_cls
        elif isinstance(raml, dict):
            value = cls.__raml_loader__(raml, class_name=class_name, filepath=filepath)

        return value

    @classmethod
    def __tree__(cls, attr_name=None, space=0):
        attr_name = attr_name or f'{{ {cls.__name__} }}'
        tree = f'{" "*space}|- {attr_name} : {cls.__bases__}{os.linesep}'
        for attr_name in getattr(cls, RAML_ATTRS):
            attr = getattr(cls, attr_name, None)
            if attr is None:
                continue
            if inspect.isclass(attr) and issubclass(attr, RamlMixin):
                try:
                    tree = tree + attr.__tree__(attr_name=attr_name, space=space+4)
                except TypeError as e:
                    raise e
            else:
                tree = tree + f'{" "*(space+4)}|- {attr_name} : {str(type(attr))}{os.linesep}'
        return tree

class RamlMetaClass(type):
    def __new__(mcs, name, bases, namespace):
        if RAML_FILE in namespace:
            bases = [base.__import_raml__(filename=namespace[RAML_FILE]) for base in bases]

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
        new_class = super().__new__(mcs, name, tuple(bases), namespace)
        return new_class

    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        setattr(obj, IS_INSTANCE, True)
        setattr(obj.__class__, ORIGIN_CLASS, cls)
        qualname = f'instance.{obj.__class__.__name__}'
        obj.__class__ = RamlMetaClass(qualname, (obj.__class__, ), obj.__dict__)
        obj.__class__.__name__ = cls.__name__
        return obj

    def __set_name__(self, owner, name):
        namespace = {ATTR_NAME: name, IS_ATTR: True}
        qualname = f'{owner.__name__}.name.{self.__name__}'
        attr_class = RamlMetaClass(qualname, (self, ), namespace)
        attr_class.__name__ = self.__name__
        setattr(attr_class, PARENTS, owner)
        setattr(owner, name, attr_class)

    # def __str__(cls):
    #     return cls.__dump_raml__()

    def __dump_raml__(self):
        pass


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
    def __raml_loader__(cls, raml, class_name=None):
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
    __property_class__ = RamlMixin
    __allowed__: _Union[_List[_Type[RamlMixin]], _Type[RamlMixin], None] = None
    __types__: dict = {}

    def __init__(self, *args, **kwargs):
        [kwargs.update(arg) for arg in args if isinstance(arg, dict)]
        annotations = dict(getattr(self, ANNOTATIONS, {}))
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
    def __raml_loader__(cls, raml, class_name=None, **kwargs):
        attrs = list(raml.keys())
        types = cls.__types__.copy()

        namespace = {}
        annotation = {}
        while len(attrs):
            attr = attrs.pop(0)
            value = raml.get(attr)

            type_name = value.get('type', None) if isinstance(value, dict) else value
            try:
                if type_name in types:
                    if isinstance(value, dict):
                        attr_cls = types[type_name].__load_raml__(value, class_name=attr, **kwargs)
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
                annotation[attr] = attr_cls
            except TypeError as e:
                print(e)


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


class Annotations:
    pass


# noinspection PyPep8Naming
class TypeMixin(RamlMixin):
    annotations: Annotations
    type: str
    displayName: str
    description: str
    enum: Enum
    facets: Facets
    default: object
    example: object
    examples: object
    xml: Xml

    # noinspection PyUnusedLocal
    def __init__(
            self, *args,
            type_: str = None,
            annotations: Annotations = None,
            displayName: str = None,
            description: str = None,
            enum: Enum = None,
            facets: Facets = None,
            default: object = None,
            example: object = None,
            examples: object = None,
            xml: Xml = None,
            **kwargs
    ):
        kwargs['type'] = kwargs.get('type', getattr(self, 'type',  type_))
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

    def __validate__(self, value):
        # todo : validation
        pass

    @classmethod
    def __tree__(cls, attr_name=None, space=0):
        tree = f'{" "*space}|- {attr_name} : {cls.type.capitalize()}{os.linesep}'
        return tree

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


class ObjectMetaClass(RamlMetaClass):
    def __new__(mcs, name, bases, namespace):
        annotation = dict(getattr(TypeMixin, ANNOTATIONS, {}))
        annotation.update(namespace.get(ANNOTATIONS, {}))
        namespace[ANNOTATIONS] = annotation

        is_dynamic_object = False
        if namespace.get('type', 'object') != 'object' and getattr(bases[0], 'type', None) == 'object':
            name = namespace['type']
            namespace[IS_DYNAMIC_OBJECT] = is_dynamic_object = True
        else:
            try:
                if bases[0] is Object and name.split('.')[-1] == 'Object':
                    namespace[IS_SINGLE_OBJECT] = True
            except NameError:
                pass

        if not namespace.get(IS_INSTANCE, False) and not namespace.get(IS_ATTR, False) or is_dynamic_object:
            properties = []
            properties_namespace = {}
            if 'Properties' in namespace.keys():
                properties_namespace[ANNOTATIONS] = {}
                for k, v in namespace['Properties'].__dict__.items():
                    if re.match('__.+__', k) or inspect.ismethod(v):
                        continue
                    properties_namespace[ANNOTATIONS][k] = v if inspect.isclass(v) else type(v)
                properties.append(namespace['Properties'])
            elif 'properties' in namespace.keys():
                namespace['Properties'] = type('Properties', (object, ), namespace['properties'].__dict__)



            type_name = []
            for base in bases:
                try:
                    if base is Object:
                        type_name.append(base.type)
                    elif issubclass(base, Object):
                        type_name.append(base.__name__)
                except NameError:
                    pass

                if hasattr(base, 'Properties'):
                    properties.append(base.Properties)

            if 'properties' in namespace.keys():
                properties.append(namespace['properties'].__class__)
            else:
                properties.append(Properties)
            properties_class = RamlMetaClass(f'Properties', tuple(properties), properties_namespace)
            namespace['properties'] = properties_class

            if type_name:
                namespace['type'] = Enum(type_name) if len(type_name) > 1 else type_name[0]

        new_class = super().__new__(mcs, name, bases, namespace)
        return new_class


# noinspection PyPep8Naming
class Object(TypeMixin, metaclass=ObjectMetaClass):
    type = 'object'
    properties: Properties
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
        kwargs['properties'] = properties
        kwargs['minProperties'] = minProperties
        kwargs['maxProperties'] = maxProperties
        kwargs['additionalProperties'] = additionalProperties
        kwargs['discriminator'] = discriminator
        kwargs['discriminatorValue'] = discriminatorValue

        super().__init__(*args, **kwargs)

    @classmethod
    def __raml_dict__(cls):

        parents = getattr(cls, PARENTS, None)
        if parents is None or issubclass(parents, Types) or getattr(cls, IS_SINGLE_OBJECT, False):
            raml = super().__raml_dict__()
        else:
            raml = cls.__name__
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
    fileTypes: Enum
    minLength: int  # default = 0
    maxLength: int  # default = 2147483647

    def __init__(
            self, *args,
            fileTypes: Enum = None,
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


class Types(Properties):
    def __init__(self, *args):
        types = {}

        def append_children(cls):
            if not inspect.isclass(cls) or not issubclass(cls, RamlMixin):
                return

            for child in getattr(cls, RAML_ATTRS, []):
                child = getattr(cls, child, None)
                append_item(child)

        def append_item(cls):
            if not inspect.isclass(cls) or not issubclass(cls, RamlMixin):
                return

            mro = list(cls.__mro__)
            mro.reverse()
            for base in mro:
                if not issubclass(base, RamlMixin) or base is RamlMixin:
                    continue
                if base in types.values():
                    continue
                append_children(base)

                if not issubclass(base, Object) or base is Object:
                    continue
                if getattr(base, IS_INSTANCE, False) or getattr(base, IS_ATTR, False):
                    continue

                types[base.__name__] = base

        for arg in args:
            append_item(arg)

        super().__init__(**types)

    @classmethod
    def append(cls):
        pass


class AnnotationTypes(Properties):
    pass


class Documentation(BaseRaml):
    title: str
    content: str


class Header(Properties):
    pass


class QueryParameter(UriParameters):
    pass


class Body(Properties):
    json: Object
    xml: Object

    __raml_attr_names__ = {
        'json': 'application/json',
        'xml': 'text/xml'
    }

    def __init__(
            self, *args,
            json: _Dict[str, _Any] = None,
            xml: _Dict[str, _Any] = None,
            **kwargs
    ):
        kwargs['json'] = Object(properties=Properties(json)) if json else None
        kwargs['xml'] = Object(properties=Properties(xml)) if xml else None
        super().__init__(*args, **kwargs)


class Responses(Properties):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# noinspection PyPep8Naming
class Response(BaseRaml):
    description: str
    annotations:  Annotations
    headers: Header
    body: Body

    def __init__(
            self, *args,
            description: str = None,
            annotations: Annotations = None,
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
    annotations: Annotations
    queryParameters: QueryParameter
    headers: Header
    queryString: Object  # The queryString and queryParameters nodes are mutually exclusive.
    responses: Responses
    body: Body
    protocols: Protocols
    is_: Enum
    securedBy: str

    __raml_attr_names__ = {'is_': 'is'}

    def __init__(
            self, *args,
            displayName: str = None,
            description: str = None,
            annotations: Annotations = None,
            queryParameters: QueryParameter = None,
            headers: Header = None,
            queryString: Object = None,
            responses: Responses = None,
            body: Body = None,
            protocols: Protocols = None,
            is_: Enum = None,
            securedBy: str = None,
            **kwargs
    ):
        kwargs['displayName'] = displayName
        kwargs['description'] = description
        kwargs['annotations'] = annotations
        kwargs['queryParameters'] = queryParameters
        kwargs['headers'] = headers
        kwargs['queryString'] = queryString
        kwargs['responses'] = responses
        kwargs['body'] = body
        kwargs['protocols'] = protocols
        kwargs['is_'] = is_
        kwargs['securedBy'] = securedBy
        super().__init__(*args, **kwargs)


class SecuredBy(BaseRaml):
    pass


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


# noinspection PyPep8Naming
class Resource(BaseRaml):
    uri: str
    displayName: str
    description: str
    annotations: Annotations
    is_: Enum
    uriParameters: UriParameters
    get: Method
    patch: Method
    put: Method
    post: Method
    delete: Method
    options: Method
    head: Method
    type: TypeMixin
    securedBy: SecuredBy
    resources: Resources

    __raml_attr_names__ = {'is_': 'is'}

    def __init__(
            self, *args,
            uri: str = None,
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
            resources: Resources = None,
            **kwargs
    ):
        kwargs['uri'] = uri
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


class Trait(Method):
    usage: str

    def __init__(
            self, *args,
            usage: str = None,
            **kwargs
    ):
        kwargs['usage'] = usage
        super().__init__(*args, **kwargs)


    @classmethod
    def __dump_raml__(cls):
        raml = super().__dump_raml__()
        raml = f'#%RAML 1.0 Trait{linesep}' \
               f'---{linesep}' \
               f'{raml}'
        return raml


trait_attrs: list = getattr(Trait, RAML_ATTRS)
trait_attrs.insert(0, trait_attrs.pop(trait_attrs.index('usage')))


class Traits(Properties):
    __property_class__ = Trait
    __allowed__ = Trait

    @classmethod
    def __raml_loader__(cls, raml, class_name=None, **kwargs):
        annotations = {}
        namespace = {}

        for k, v in raml.items():
            property_class = cls.__property_class__.__load_raml__(v, class_name=class_name, **kwargs)
            annotations[k] =  property_class
            namespace[k] = property_class
        namespace[ANNOTATIONS] = annotations
        raml_cls = type(class_name or cls.__name__, (cls, ), namespace)
        return raml_cls







# load from raml file
class Uses(Properties):
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


class Api(BaseRaml):
    title: str
    description: str
    version: str
    baseUri: str
    baseUriParameters: UriParameters
    protocols: Protocols
    mediaType: MediaType
    documentation: Documentation
    uses: Uses
    types: Types
    traits: Traits
    resourceTypes: object
    annotations: Annotations
    securitySchemes: object
    securedBy: object
    resources: Resources
    extends: str

    @classmethod
    def __raml_dict__(cls):
        raml = super().__raml_dict__()
        resources: dict = raml.pop('resources', {})
        if resources:
            raml.update(resources)
        return raml

    @classmethod
    def __dump_raml__(cls):
        raml = super().__dump_raml__()
        raml = f'#%RAML 1.0{linesep}' \
               f'---{linesep}' \
               f'{raml}'
        return raml


def str_presenter(dumper, data):
    data = data.strip()
    if len(data.splitlines()) > 1:  # check for multiline string
        data = f'{os.linesep}'.join([re.sub("(^(\\s{4})+)|(\\s+$)", '', s) for s in data.split(os.linesep)])
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


yaml.add_representer(str, str_presenter)


def tuple_presenter(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)


yaml.add_representer(tuple, tuple_presenter)
