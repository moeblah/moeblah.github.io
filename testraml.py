import yaml
from typing import Type as _Type
from tests.utiles.raml.pyraml import *


def str_presenter(dumper, data):
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


yaml.add_representer(str, str_presenter)


class BaseUriParameters(UriParameters):
    domain: Any = Any(description='Domain or IP')
    port: Integer = Integer(description='Connection port')


class DocumentationHome(DocumentationItem):
    title = 'Home'
    content = '''Welcome to the _Zencoder API_ Documentation. The _Zencoder API_
 allows you to connect your application to our encoding service
 and encode videos without going through the web  interface. You
 may also benefit from one of our
 [integration libraries](https://app.zencoder.com/docs/faq/basics/libraries)
 for different languages.'''


class DocumentationLegal(DocumentationItem):
    title = 'Legal'
    content = '''Legal Content'''



class Person(Object):
    description = '사람'

    # noinspection PyPep8Naming
    class properties:
        name: String  = String(description="이름")
        age: Integer = Integer(description="나이")

class Employee(Person):

    # noinspection PyPep8Naming
    class properties:
        id: String = String(description="아이디")


class HasHome(Object):
    # noinspection PyPep8Naming
    class properties:
        homeAddress: String = String()

class Cat(Object):
    # noinspection PyPep8Naming
    class properties:
        name: String = String()
        color: String = String()

class Dog(Object):
    # noinspection PyPep8Naming
    class properties:
        name: String = String()
        fangs: String = String()

class HomeAnimal(HasHome, Cat):
    pass



# noinspection PyStatementEffect
class TestApiTypes(Types):
    Person: _Type[Object] = Object(
        description = "사람",
        properties = Properties.make(
            name = String(description='이름'),
            age = Integer()
        )
    )



class TestApi(Api):
    title = 'Test Api'
    description = 'Test Api description'
    version = '1.0'
    baseUri = 'https://{domain}:{port}/{version}/'
    baseUriParameters = BaseUriParameters
    protocols = ['HTTP', 'HTTPS']
    mediaType = 'application/json'
    documentation = [DocumentationHome, DocumentationLegal]
    types = TestApiTypes


print(
    f'''#%RAML 1.0{
    yaml.dump(
        TestApi.to_raml(),
        default_flow_style=False, 
        allow_unicode=True
    )
    }
    '''
)
a = TestApi()
c = a.baseUriParameters
t = TestApiTypes()
d = TestApiTypes.Person()
d.properties.name = 'abcd'
t.Person = d.properties
pass
