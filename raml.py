from typing import Type, List, Dict, Union, TypeVar

T_API = TypeVar('T_API', bound='API')
T_DocumentationItem = TypeVar('T_DocumentationItem', bound='DocumentationItem')
T_Resource = TypeVar('T_Resource', bound='Resource')
T_Method = TypeVar('T_Method', bound='Method')
T_Response = TypeVar('T_Response', bound='Response')
T_RequestBody = TypeVar('T_RequestBody', bound='RequestBody')
T_ResponseBody = TypeVar('T_ResponseBody', bound='ResponseBody')
# todo : Create TypeDeclaration Class
T_TypeDeclaration = TypeVar('T_TypeDeclaration', bound='TypeDeclaration')
T_Facets = TypeVar('T_Facets', bound='Facets')
T_Example = TypeVar('T_Example', bound='Example')
T_ResourceType = TypeVar('T_ResourceType', bound='ResourceType')
T_Trait = TypeVar('T_Trait', bound='Trait')
T_SecurityScheme = TypeVar('T_SecurityScheme', bound='SecurityScheme')
T_SecuritySchemeSettings = TypeVar('T_SecuritySchemeSettings', bound='SecuritySchemeSettings')
T_AnnotationType = TypeVar('T_AnnotationType', bound='AnnotationType')
T_Library = TypeVar('T_Library', bound='Library')
T_Overlay = TypeVar('T_Overlay', bound='Overlay')
T_Extension = TypeVar('T_Extension', bound='Extension')

class RamlMetaClass(type):
    def __new__(mcs, name, bases, namespace):
        return super().__new__(name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        
    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        return obj

    def __set_name__(self, owner, name):
        setattr(self, '__attr_name__', name)
        pass

    def __get__(self, instance, owner):
        pass

    def __set__(self, instance, value):
        pass


class BaseRaml(metaclass=RamlMetaClass):
    def __get__(self, instance, owner):
        pass

    def __set__(self, instance, value):
        pass


class Annotation(BaseRaml):
    allowedTargets: List[Union[Type[], Type[]]]
    pass


class AnnotationTypes(BaseRaml):
    pass


class Xml(BaseRaml):
    attribute: bool                 # default false
    wrapped: bool                   # default false
    name: str
    namespace: str
    prefix: str




class Any(BaseRaml):
    type: str = None
    annotations: List[Annotation]
    displayName: str
    description: str
    enum: List[object]
    facets: Type[T_Facets]
    default: object
    example: object
    examples: object
    xml: Type[Xml]


class Properties(BaseRaml):
    __allowed__: Union[None, Type[BaseRaml], List[BaseRaml]] = Any
    pass


class Facets(Properties):
    pass


class Types(Properties):
    pass


class Object(Any):
    type = 'object'
    properties: Type[Properties]
    minProperties: object
    maxProperties: object
    additionalProperties: bool      # default true
    discriminator: str
    discriminatorValue: str         # default The name of type


class Array(Any):
    type = 'array'
    uniqueItems: bool
    items: Type[Any]
    minItems: int                   # default 0
    maxItems: int                   # default 2147483647


class String(Any):
    type = 'string'
    minLength: int                  # default 0
    maxLength: int                  # default 2147483647
    pattern: str                    # Regular expression


class Number(Any):
    type = 'number'
    minimum: int
    maximum: int
    format: str
    multipleOf: int


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


class Datetime(Any):
    type = 'datetime'
    format: str                     # default RFC3339 yyyy-mm-ddThh:mm:ss[.ff...]Z


class DatetimeOnly(Datetime):
    type = 'datetime-only'          # default RFC3339 yyyy-mm-ddThh:mm:ss[.ff...]


class DateOnly(Datetime):
    type = 'date-only'              # default RFC3339 yyyy-mm-dd


class TimeOnly(Datetime):
    type = 'time-only'              # default RFC3339 hh:mm:ss[.ff...]


class File(Any):
    type = 'file'
    fileTypes: List[str]
    minLength: int                  # default = 0
    maxLength: int                  # default = 2147483647


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


class Response(BaseRaml):
    description: str
    annotations: List[Annotation]
    headers: Type[Header]
    body: Type[Body]




class Method(BaseRaml):
    displayName: str
    description: str
    annotations: List[Annotation]
    queryParameters: Type[QueryParameter]
    headers: Type[Header]
    queryString: Type[Object]       # The queryString and queryParameters nodes are mutually exclusive.
    response: Type[Response]
    body: Type[Body]
    protocols: List[str]
    is_: Type[T_Trait]
    securedBy: str


class Trait(Method):
    usage: str


class Traits(Properties):
    __allowed__ = Trait


class Resource(BaseRaml):
    uris: Union[str, List[str]]
    displayName: str
    description: str
    annotations: List[Annotation]
    get: Type[Method]
    patch: Type[Method]
    put: Type[Method]
    post: Type[Method]
    delete: Type[Method]
    options: Type[Method]
    head: Type[Method]


# load from raml file
class Uses(Properties):
    __allowed__ = [Types, 'ResourceTypes', Traits, 'SecuritySchemes', AnnotationTypes, ]


class API(BaseRaml):
    title: str
    description: str
    version: str
    baseUri: str
    baseUriParameters: Type[UriParameters]
    protocols: List[str]
    mediaType: Union[str, List[str]]
    documentation: List[DocumentationItem]
    types: Type[Types]
    traits: Type[Traits]
    resourceTypes: object
    annotations: List[Annotation]
    securitySchemes: object
    securedBy: object
    uses: Type[Uses]
    resources: List[Resource]
