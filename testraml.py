import os
from tests.apps import RAML_ROOT_PATH
from tests.utiles.raml.pyraml import *

# from tests.apps.traits.secured import TraitSecured

class MonitorRoutes(Object):
    properties = Properties(
        count = Number(description='라우팅 목록 수'),
        rlist = Array(description='라우팅 목록', items=Object(properties=Properties(
            id = Number(),
            protocol = Integer(
                description=''' 
                프로토콜<br/>
                
                값 | 설명
                :---:|:---
                0 | all
                1 | static
                2 | direct
                3 | RIP
                4 | BGP
                5 | OSPF
                6 | RIPng
                7 | OSPFv3
                8 | RA''', enum=Enum(0, 1, 2, 3, 4, 5, 6, 7, 8)
            ),
            dest = String(description='목적지 네트워크'),
            ad = String(description='관리 거리'),
            metric = String(description='메트릭'),
            gw = Array(description='케이트웨이 목록', items=Object(properties=Properties(
                addr = String(description='게이트웨이 주소'),
                ifc_id = String(description='게이트웨이 인터페이스 아이디'),
                ifc_name = String(description='게이트웨이 인터페이스 이름'),
            ))),
            rout_type = Number()
        )))
    )

    class Properties:
        pass


class ResourceRoutingStatus(Resource):
    displayName = '라우팅 현황'
    uri = '/routing-status'

    resources = Resources(
        Resource(
            uri='/routings',
            displayName='라우팅 현황 조회',
            description='라우팅 현황을 조회한다.',
            is_= Enum({'Secured': {'description': '라우팅현황'}}),
            post=Method(
                displayName='라우팅 현황을 등록한다.'
            ),
            get=Method(
                displayName='라우팅 현황을 조회한다.',
                queryParameters=QueryParameter(
                    max_page=Integer(description='페이지당 건수'),
                    page=Integer(description='현재 페이지 수'),
                    table_id=Int8(
                        description='라우팅테이블 번호 (GET_MONITOR_TABLES로 얻어온 테이블 아이디)',
                        minimum=0, maximum=255
                    ),
                    protocol=Int8(
                        description='''
                        프로토콜
                        
                        값 | 설명
                        :---:|:---
                         0 |  all    
                         1 | static
                         2 | direct
                         3 | RIP
                         4 | BGP
                         5 | OSPF
                         6 | RIPng
                         7 | OSPFv3
                         8 | RA''',
                        enum=Enum(1, 2, 3, 4, 5, 6, 7, 8)
                    ),
                    route_type=Int8(
                        description='''라우트 타입
                        
                        값 | 설명
                        :---:|:---
                         0 | ALL 
                         1 | UNICAST 
                         6 | BLACKHOLE 
                         7 | UNREACHABLE 
                         8 | PROHIBIT''',
                        enum=Enum(0, 1, 6, 7, 8)
                    ),
                    dest_addr=String(description='검색 목적지 네트워크 주소 (IPv4 주소 형식)'),
                    dest_mask=String(description='검색 목적지 네트워크 마스크 길이 (0~32)', minLength=0, maxLength=32),
                ),
                responses=Responses({
                    '200': Response(body=Body(
                        json={'result':MonitorRoutes()}
                    ))
                })
            ),
            resources=Resources(
                Resource(
                    uri='/entry',
                    description='라우팅 현황 삭제',
                    get=Method(
                        descriptoin='라우팅 형황을 삭제한다.'
                    )
                ),
            )
        ),
        Resource(
            uri='/tables',
            displayName='라우팅 현황  정적/정책 테이블 조회',
        ),
        Resource(
            uri='/lookup-route',
            displayName=' 라우팅 룩업경로 조회',
        ),
    )

class ApiRoutingSetting(Api):
    # __raml_file__ = os.path.join(RAML_ROOT_PATH, 'rest', 'sm', 'oe', 'routing_DEV.raml')
    # __export_file__ = __raml_file__

    title = '라우팅설정'
    baseUri = 'http://{host}/api/sm'
#     baseUriParameters = UriParameters(url=String(description = '장비 IP:Port'))
    protocols = Protocols(Protocols.http)
    mediaType = MediaType(MediaType.json)

    # traits = Traits(Secured=TraitSecured)
    # users = Uses(Lib='routing_INFO.raml')
#    types = Types(MonitorRoutes)

#    resources = Resources(ResourceRoutingStatus)


print(ApiRoutingSetting.__raml_dict__())

# print(ApiRoutingSetting.dump_raml())
# ApiRoutingSetting.export_raml()

'''
정적 라우팅	엔트리 목록 조회	GET	/static-routings
	엔트리 추가	POST	/static-routings
	엔트리 목록 삭제(멀티 선택)	DELETE	/static-routings
	단일 엔트리 조회	GET	/static-routings/<pk>
	단일 엔트리 수정	PUT	/static-routings/<pk>
	단일 엔트리 삭제	DELETE	/static-routings/<pk>
	게이트웨이 인터페이스 후보 목록 조회	GET	/static-routings/interface-candidates
	정적 라우팅 배치	POST	/static-routings/batch
	동적 라우팅 목록 조회	GET	/dynamic-routings
	직접 연결된 라우팅 목록 조회	GET	/direct-routings
정책 라우팅	라우팅 마커 목록 조회	GET	/routing-markers
	라우팅 마커 추가	POST	/routing-markers
	라우팅 마커 목록 삭제(멀티 선택)	DELETE	/routing-markers
	단일 라우팅 마커 조회	GET	/routing-markers/<pk>
	단일 라우팅 마커 삭제	DELETE	/routing-markers/<pk>
	라우팅 마커 된 방화벽 정책 목록 조회	GET	/routing-markers/<pk>/fws
	라우팅 마커 된 라우팅 정책 목록 조회	GET	/routing-markers/<pk>/rps
	정책 테이블 목록 조회	GET	/policy-tables
	정책 테이블 추가	POST	/policy-tables
	정책 테이블 목록 삭제(멀티 선택)	DELETE	/policy-tables
	단일 정책 테이블 조회	GET	/policy-tables/<pk>
	단일 정책 테이블 수정	PUT	/policy-tables/<pk>
	단일 정책 테이블 삭제	DELETE	/policy-tables/<pk>
	정책 테이블 엔트리 목록 조회	GET	/policy-tables/<ppk>/entries
	정책 테이블 엔트리 추가	POST	/policy-tables/<ppk>/entries
	정책 테이블 엔트리 목록 삭제(멀티 선택)	DELETE	/policy-tables/<ppk>/entries
	단일 정책 테이블 엔트리 조회	GET	/policy-tables/<ppk>/entries/<pk>
	단일 정책 테이블 엔트리 수정	PUT	/policy-tables/<ppk>/entries/<pk>
	단일 정책 테이블 엔트리 삭제	DELETE	/policy-tables/<ppk>/entries/<pk>
	라우팅 정책 목록 조회	GET	/routing-policies
	라우팅 정책 추가	POST	/routing-policies
	라우팅 정책 목록 삭제(멀티 선택)	DELETE	/routing-policies
	단일 라우팅 정책 조회	GET	/routing-policies/<pk>
	단일 라우팅 정책 수정	PUT	/routing-policies/<pk>
	단일 라우팅 정책 삭제	DELETE	/routing-policies/<pk>
RIP	RIP 설정 조회	GET	/rip/config
	RIP 설정 수정	PUT	/rip/config
	상태 정보 조회	GET	/rip/config/status
	고급 설정 조회	GET	/rip/config/advance
	고급 설정 수정	PUT	/rip/config/advance
	Route 인터페이스 후보 목록 조회	GET	/rip/config/interface-candidates
	네트워크 목록 조회	GET	/rip/config/networks
	네트워크 추가	POST	/rip/config/networks
	네트워크 목록 삭제(멀티 선택)	DELETE	/rip/config/networks
	단일 네트워크 조회	GET	/rip/config/networks/<pk>
	단일 네트워크 수정	PUT	/rip/config/networks/<pk>
	단일 네트워크 삭제	DELETE	/rip/config/networks/<pk>
	적용	PUT	/rip/config/apply
	취소	PUT	/rip/config/cancel
BGP	BGP 설정 조회	GET	/bgp/config
	BGP 설정 수정	PUT	/bgp/config
	상태 정보 조회	GET	/bgp/config/status
	Neighbor 상태 정보 조회	GET	/bgp/config/status-neighbor
	고급 설정 조회	GET	/bgp/config/advance
	고급 설정 수정	PUT	/bgp/config/advance
	네트워크 목록 조회	GET	/bgp/config/networks
	네트워크 추가	POST	/bgp/config/networks
	네트워크 목록 삭제(멀티 선택)	DELETE	/bgp/config/networks
	단일 네트워크 조회	GET	/bgp/config/networks/<pk>
	단일 네트워크 수정	PUT	/bgp/config/networks/<pk>
	단일 네트워크 삭제	DELETE	/bgp/config/networks/<pk>
	인접 라우터 IP 목록 조회	GET	/bgp/config/neighbors
	인접 라우터 IP 추가	POST	/bgp/config/neighbors
	인접 라우터 IP 목록 삭제(멀티 선택)	DELETE	/bgp/config/neighbors
	단일 인접 라우터 IP 조회	GET	/bgp/config/neighbors/<pk>
	단일 인접 라우터 IP 수정	PUT	/bgp/config/neighbors/<pk>
	단일 인접 라우터 IP 삭제	DELETE	/bgp/config/neighbors/<pk>
	적용	PUT	/bgp/config/apply
	취소	PUT	/bgp/config/cancel
OSPF	OSPF 설정 조회	GET	/ospf/config
	OSPF 설정 수정	PUT	/ospf/config
	상태 정보 조회	GET	/ospf/config/status
	Neighbor 상태 정보 조회	GET	/ospf/config/status-neighbor
	Interface 상태 정보 조회	GET	/ospf/config/status-interface
	Database 상태 정보 조회	GET	/ospf/config/status-database
	고급 설정 조회	GET	/ospf/config/advance
	고급 설정 수정	PUT	/ospf/config/advance
	Area 목록 조회	GET	/ospf/config/areas
	Area 추가	POST	/ospf/config/areas
	Area 목록 삭제(멀티 선택)	DELETE	/ospf/config/areas
	단일 Area 조회	GET	/ospf/config/areas/<pk>
	단일 Area 삭제	DELETE	/ospf/config/areas/<pk>
	네트워크 목록 조회	GET	/ospf/config/networks
	네트워크 추가	POST	/ospf/config/networks
	네트워크 목록 삭제(멀티 선택)	DELETE	/ospf/config/networks
	단일 네트워크 조회	GET	/ospf/config/networks/<pk>
	단일 네트워크 수정	PUT	/ospf/config/networks/<pk>
	단일 네트워크 삭제	DELETE	/ospf/config/networks/<pk>
	OSPF 인터페이스 후보 목록 조회	GET	/ospf/config/interface-candidates
	인터페이스 목록 조회	GET	/ospf/config/interfaces
	인터페이스 추가	POST	/ospf/config/interfaces
	인터페이스 목록 삭제(멀티 선택)	DELETE	/ospf/config/interfaces
	단일 인터페이스 조회	GET	/ospf/config/interfaces/<pk>
	단일 인터페이스 수정	PUT	/ospf/config/interfaces/<pk>
	단일 인터페이스 삭제	DELETE	/ospf/config/interfaces/<pk>
	적용	PUT	/ospf/config/apply
	취소	PUT	/ospf/config/cancel
SECUI RIP	SECUI RIP 설정 조회	GET	/secui-rip/config
	SECUI RIP 설정 수정	PUT	/secui-rip/config
	회선 인터페이스 후보 목록 조회	GET	/secui-rip/config/interface-candidates
	HA 회선 인터페이스 후보 목록 조회	GET	/secui-rip/config/ha-interface-candidates
	HA 우선 순위 IP 후보 목록 조회	GET	/secui-rip/config/ha-ip-candidates
	RIP HA 목록 조회	GET	/secui-rip/config/has
	RIP HA 추가	POST	/secui-rip/config/has
	RIP HA 목록 삭제(멀티 선택)	DELETE	/secui-rip/config/has
	단일 RIP HA 조회	GET	/secui-rip/config/has/<pk>
	단일 RIP HA 수정	PUT	/secui-rip/config/has/<pk>
	단일 RIP HA 삭제	DELETE	/secui-rip/config/has/<pk>
	적용	PUT	/secui-rip/config/apply
	취소	PUT	/secui-rip/config/cancel

'''
