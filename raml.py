import re
import inspect

from typing import (
    Type as _Type, List as _List, Dict as _Dict,
    Union as _Union, TypeVar as _TypeVar, Generic as _Generic,
    Callable as _Callable,
)

_T = _TypeVar('_T')
T_BaseRaml= _TypeVar('T_BaseRaml', bound='BaseRaml')
T_API = _TypeVar('T_API', bound='API')
T_DocumentationItem = _TypeVar('T_DocumentationItem', bound='DocumentationItem')
T_Resource = _TypeVar('T_Resource', bound='Resource')
T_Method = _TypeVar('T_Method', bound='Method')
T_Response = _TypeVar('T_Response', bound='Response')
T_RequestBody = _TypeVar('T_RequestBody', bound='RequestBody')
T_ResponseBody = _TypeVar('T_ResponseBody', bound='ResponseBody')
# todo : Create TypeDeclaration Class
# T_TypeDeclaration = _TypeVar('T_TypeDeclaration', bound='TypeDeclaration')

T_Type = _TypeVar('T_Type', bound='Type')
T_Facets = _TypeVar('T_Facets', bound='Facets')
# T_Example = _TypeVar('T_Example', bound='Example')
# T_ResourceType = _TypeVar('T_ResourceType', bound='ResourceType')
T_Trait = _TypeVar('T_Trait', bound='Trait')
# T_SecurityScheme = _TypeVar('T_SecurityScheme', bound='SecurityScheme')
# T_SecuritySchemeSettings = _TypeVar('T_SecuritySchemeSettings', bound='SecuritySchemeSettings')
# T_AnnotationType = _TypeVar('T_AnnotationType', bound='AnnotationType')
T_AnnotationTypes = _TypeVar('T_AnnotationTypes', bound='AnnotationTypes')
# T_Library = _TypeVar('T_Library', bound='Library')
# T_Overlay = _TypeVar('T_Overlay', bound='Overlay')
# T_Extension = _TypeVar('T_Extension', bound='Extension')


"""
def load_raml(filename) -> _Type[T_BaseRaml]:
    pass

def include(filename) -> _Type[T_BaseRaml]:
    pass

def extends(filename) -> _Type[T_BaseRaml]:
    pass

def overwrite(filename) -> _Type[T_BaseRaml]:
    pass
"""

class RamlMetaClass(type):
    def __new__(mcs, name, bases, namespace):
        attributes : dict = namespace.get('__annotations__', {})
        attributes = attributes.copy()
        for base in bases:
            if issubclass(base, BaseRaml):
                base_attributes: dict = getattr(base, '__raml_attributes__', {})
                base_attributes = base_attributes.copy()
                base_attributes.update(attributes)
                attributes = base_attributes

        for key in list(attributes.keys()):
            if re.match('__.+__', key):
                attributes.pop(key)

        namespace['__raml_attributes__'] = attributes
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)

    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        return obj

    def __set_name__(self, owner, name):
        print (f'RamlMetaClass.__set_name__({owner}, {name}) <- {self}')
        setattr(self, '__attr_name__', name)

    def __get__(self, instance, owner):
        print (f'RamlMetaClass.__get__({instance}, {owner}) <- {self}')
        return self

    '''
    def __set__(self, instance, value):
        pass
    '''


class BaseRaml(metaclass=RamlMetaClass):

    def __init__(self, *args, **kwargs):
        for key, item in kwargs.items():
            setattr(self, key, item)

    """
    def __get__(self, instance, owner):
        pass

    def __set__(self, instance, value):
        pass
    """

    def __set_name__(self, owner, name):
        print (f'BaseRaml.__set_name__({owner}, {name}) <- {self}')
        cls = RamlMetaClass(name, (self.__class__, ), self.__dict__)
        setattr(owner, name, cls)


    @classmethod
    def to_raml(cls):
        raml = {}
        attributes = getattr(cls, '__raml_attributes__', {})
        for attr in attributes.keys():
            value: _Union[_Type[_T], object] = getattr(cls, attr, None)
            if inspect.isclass (value) and issubclass(value, BaseRaml):
                value = value.to_raml()
            raml[attr] = value
        return raml


class RamlList(BaseRaml):
    __items__: _List[BaseRaml]

    def append(self, obj:BaseRaml):
        self.__items__.append(obj)

    def insert(self, index: int, obj:BaseRaml):
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
    __allowed__: _Union[None, _Type[BaseRaml], _List[BaseRaml]] = None


class Facets(Properties):
    pass


class AnnotationTypes(Properties):
    pass


class Types(Properties):
    pass

# noinspection PyPep8Naming
class Type(BaseRaml):
    annotations: _List[_Type[T_Type]]
    type: str
    displayName: str
    description: str
    enum: _List[object]
    facets: _Type[Facets]
    default: object
    example: object
    examples: object
    xml: _Type[Xml]

    def __init__(self, *args,
                 type_:str=None,
                 annotations:_List[_Type[T_Type]]=None,
                 displayName:str=None,
                 description:str=None,
                 enum:_List[object]=None,
                 facets:_Type[Facets]=None,
                 default:object=None,
                 example:object=None,
                 examples:object=None,
                 xml:_Type[Xml]=None,
                 **kwargs
                 ):
        kwargs['type'] = type_
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


Properties.__allowed__ = Type


# noinspection PyPep8Naming
class Any(Type):
    pass



# noinspection PyPep8Naming
class Object(Type):
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
            properties:_Type[Properties]=None,
            minProperties:object=None,
            maxProperties:object=None,
            additionalProperties:bool=None,
            discriminator:str=None,
            discriminatorValue:str=None,
            **kwargs
    ):
        kwargs['properties'] = properties
        kwargs['minProperties'] = minProperties
        kwargs['maxProperties'] = maxProperties
        kwargs['additionalProperties'] = additionalProperties
        kwargs['discriminator'] = discriminator
        kwargs['discriminatorValue'] = discriminatorValue
        super().__init__(*args, **kwargs)


# noinspection PyPep8Naming
class Array(Type):
    type = 'array'
    uniqueItems: bool
    items: _Type[Type]
    minItems: int                           # default 0
    maxItems: int                           # default 2147483647

    def __init__(self, *args,
                 uniqueItems:bool=None,
                 items:_Type[Type]=None,
                 minItems:int=None,
                 maxItems:int=None,
                 **kwargs
     ):
        kwargs['uniqueItems'] = uniqueItems
        kwargs['items'] = items
        kwargs['minItems'] = minItems
        kwargs['maxItems'] = maxItems
        super().__init__(*args, **kwargs)


# noinspection PyPep8Naming
class String(Type):
    type = 'string'
    minLength: int  # default 0
    maxLength: int  # default 2147483647
    pattern: str  # Regular expression

    def __init__(self, *args,
                 minLength:int=None,
                 maxLength:int=None,
                 pattern:str=None,
                 **kwargs
    ):
        kwargs['minLength'] = minLength
        kwargs['maxLength'] = maxLength
        kwargs['pattern'] = pattern
        super().__init__(*args, **kwargs)


# noinspection PyPep8Naming
class Number(Type):
    type = 'number'
    minimum: int
    maximum: int
    format: str
    multipleOf: int

    def __init__(self, *args,
                 minimum:int=None,
                 maximum:int=None,
                 format_:str=None,
                 multipleOf:int=None,
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


class Boolean(Type):
    type = 'boolean'


# noinspection PyPep8Naming
class Datetime(Type):
    type = 'datetime'
    format: str  # default RFC3339 yyyy-mm-ddThh:mm:ss[.ff...]Z
    def __init__(self, *args, format_:str=None, **kwargs):
        kwargs['format'] = format_
        super().__init__(*args, **kwargs)


class DatetimeOnly(Datetime):
    type = 'datetime-only'  # default RFC3339 yyyy-mm-ddThh:mm:ss[.ff...]


class DateOnly(Datetime):
    type = 'date-only'  # default RFC3339 yyyy-mm-dd


class TimeOnly(Datetime):
    type = 'time-only'  # default RFC3339 hh:mm:ss[.ff...]


# noinspection PyPep8Naming
class File(Type):
    type = 'file'
    fileTypes: _List[str]
    minLength: int  # default = 0
    maxLength: int  # default = 2147483647
    def __init__(self, *args,
                 fileTypes:_List[str]=None,
                 minLength:int=None,
                 maxLength:int=None,
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
    type = None


# noinspection PyPep8Naming
class Response(BaseRaml):
    description: str
    annotations: _List[_Type[Type]]
    headers: _Type[Header]
    body: _Type[Body]

    def __init__(self, *args,
                 description: str = None,
                 annotations: _List[_Type[Type]] = None,
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
    annotations: _List[_Type[Type]]
    queryParameters: _Type[QueryParameter]
    headers: _Type[Header]
    queryString: _Type[Object]  # The queryString and queryParameters nodes are mutually exclusive.
    response: _Type[Response]
    body: _Type[Body]
    protocols: _List[str]
    is_: _Type[T_Trait]
    securedBy: str

    def __init__(self, *args,
                 displayName:str=None,
                 description:str=None,
                 annotations:_List[_Type[Type]]=None,
                 queryParameters:_Type[QueryParameter]=None,
                 headers:_Type[Header]=None,
                 queryString:_Type[Object]=None,
                 response:_Type[Response]=None,
                 body:_Type[Body]=None,
                 protocols:_List[str]=None,
                 is_: _Type[T_Trait]=None,
                 securedBy:str=None,
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


class Trait(Method):
    usage: str
    def __init__(self, *args, usage:str=None, **kwargs):
        kwargs['usage'] = usage
        super().__init__(*args, **kwargs)


class Traits(Properties):
    __allowed__ = Trait


# noinspection PyPep8Naming
class Resource(BaseRaml):
    uris: _Union[str, _List[str]]
    displayName: str
    description: str
    annotations: _List[_Type[Type]]
    get: _Type[Method]
    patch: _Type[Method]
    put: _Type[Method]
    post: _Type[Method]
    delete: _Type[Method]
    options: _Type[Method]
    head: _Type[Method]
    resources: _List[_Type[T_Resource]]

    def __init__(self, *args,
                 uris:_Union[str, _List[str]]=None,
                 displayName:str=None,
                 description:str=None,
                 annotations:_List[_Type[Type]]=None,
                 get:_Type[Method]=None,
                 patch:_Type[Method]=None,
                 put:_Type[Method]=None,
                 post:_Type[Method]=None,
                 delete:_Type[Method]=None,
                 options:_Type[Method]=None,
                 head:_Type[Method]=None,
                 resources:_List[_Type[T_Resource]]=None,
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
    __allowed__ = [Types, 'ResourceTypes', Traits, 'SecuritySchemes', AnnotationTypes, ]


class API(BaseRaml):
    title: str
    description: str
    version: str
    baseUri: str
    baseUriParameters: _Type[UriParameters]
    protocols: _List[str]
    mediaType: _Union[str, _List[str]]
    documentation: _List[DocumentationItem]
    types: _Type[Types]
    traits: _Type[Traits]
    resourceTypes: object
    annotations: _List[_Type[Type]]
    securitySchemes: object
    securedBy: object
    uses: _Type[Uses]
    resources: _List[Resource]
    extends: str                                # raml file name todo:

