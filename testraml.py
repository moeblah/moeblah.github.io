import yaml
from pyraml.raml import *


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


class TestApi(Api):
    title = 'Test Api'
    description = 'Test Api description'
    version = '1.0'
    baseUri = 'https://{domain}:{port}/{version}/'
    baseUriParameters = BaseUriParameters
    protocols = ['HTTP', 'HTTPS']
    mediaType = 'application/json'
    documentation = [DocumentationHome, DocumentationLegal]


print(
    f'''#%RAML 1.0{
    yaml.dump(
        TestApi.to_raml(),
        default_flow_style=False, sort_keys=False,
        allow_unicode=True
    )
    }
    '''
)
