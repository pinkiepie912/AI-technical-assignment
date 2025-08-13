"""Test fixtures for Forest of Hyuksin reader tests"""
import pytest
from datetime import date
from uuid import UUID, uuid4

from enrichment.domain.entities.company import Company
from enrichment.domain.entities.company_alias import CompanyAlias
from enrichment.domain.entities.company_metrics_snapshot import CompanyMetricsSnapshot
from enrichment.domain.aggregates.company_aggregate import CompanyAggregate
from enrichment.domain.vos.metrics import MonthlyMetrics


@pytest.fixture
def complete_forest_of_hyuksin_data():
    """Complete valid Forest of Hyuksin data structure based on 밀리의서재 example"""
    return {
        "mau": {
            "list": [
                {
                    "data": [
                        {
                            "value": 726765,
                            "growthRate": None,
                            "referenceMonth": "2022-03"
                        },
                        {
                            "value": 565191,
                            "growthRate": -22.2,
                            "referenceMonth": "2022-04"
                        }
                    ],
                    "manual": False,
                    "productId": "PD00000221"
                }
            ],
            "recentUpdate": "2025-02-25"
        },
        "patent": {
            "list": [
                {
                    "level": "C",
                    "title": "감성 태그 기반의 도서평 제공 장치",
                    "registerAt": "2018-11-16"
                }
            ],
            "chart": [
                {
                    "count": 1,
                    "level": "C"
                }
            ],
            "words": [
                {
                    "text": "태그",
                    "patentCount": 1,
                    "displayCount": 16
                }
            ],
            "totalCount": 1,
            "averageRank": 2.0,
            "recentUpdate": "2022-01-25"
        },
        "finance": {
            "data": [
                {
                    "type": "SEPARATE_NICE",
                    "year": 2021,
                    "profit": 28856986000,
                    "capital": 1366560000,
                    "netProfit": -34841769000,
                    "liabilities": 100833247000,
                    "totalAssets": 17843206000,
                    "totalCapital": -82990041000,
                    "operatingProfit": -14510621000
                },
                {
                    "type": "SEPARATE_NICE",
                    "year": 2022,
                    "profit": 45829674000,
                    "capital": 3283455000,
                    "netProfit": 13349631000,
                    "liabilities": 20032681000,
                    "totalAssets": 27570195000,
                    "totalCapital": 7537514000,
                    "operatingProfit": 4169062000
                }
            ],
            "recentUpdate": "2025-02-25"
        },
        "products": [
            {
                "id": "PD00000221",
                "name": "밀리의서재",
                "types": [
                    {
                        "url": "https://play.google.com/store/apps/details?id=kr.co.millie.millieshelf",
                        "type": "APP"
                    },
                    {
                        "type": "IOS"
                    },
                    {
                        "url": "millie.co.kr",
                        "type": "WEB"
                    }
                ],
                "finishedAt": None,
                "logoImgUrl": "https://lh3.googleusercontent.com/ck3EZc2bX63rxRC-aMdx46T-KcZiFtm8QxLLY81Yi8ej3mHv7xdBNWe_eT55s1Usa8AI"
            }
        ],
        "investment": {
            "data": [
                {
                    "level": "IPO",
                    "investAt": "2023-09-27",
                    "investor": [
                        {
                            "id": "IV00001754",
                            "name": "KOSDAQ",
                            "hasLink": False
                        }
                    ],
                    "investmentAmount": 34500000000
                },
                {
                    "level": "series C",
                    "investAt": "2019-05-01",
                    "investor": [
                        {
                            "id": "IV00001148",
                            "name": "에이치비인베스트먼트",
                            "hasLink": True
                        },
                        {
                            "id": "IV00001705",
                            "name": "케이비인베스트먼트",
                            "hasLink": True
                        }
                    ],
                    "investmentAmount": 18200000000
                }
            ],
            "recentUpdate": "2023-10-04",
            "lastInvestmentLevel": "IPO",
            "investmentDescription": "",
            "totalInvestmentAmount": 62650000000
        },
        "customerType": {
            "salesFamily": [
                {
                    "rate": 5.4,
                    "type": "성인자녀가구"
                },
                {
                    "rate": 55.2,
                    "type": "싱글가구"
                }
            ],
            "salesIncome": [
                {
                    "rate": 1.7,
                    "type": "2000만원이하"
                },
                {
                    "rate": 17.2,
                    "type": "3000만원이하"
                }
            ],
            "salesPerson": [
                {
                    "rate": 12.5,
                    "gender": "여성",
                    "ageGroup": "40~49세"
                },
                {
                    "rate": 17.9,
                    "gender": "여성",
                    "ageGroup": "20~29세"
                }
            ],
            "recentUpdate": "2025-02-24"
        },
        "organization": {
            "data": [
                {
                    "in": 4,
                    "out": 6,
                    "value": 188,
                    "growRate": -0.5,
                    "referenceMonth": "2025-01"
                },
                {
                    "in": 14,
                    "out": 5,
                    "value": 189,
                    "growRate": 6.2,
                    "referenceMonth": "2024-12"
                }
            ],
            "retireRate": 29.1,
            "recentUpdate": "2025-02-24"
        },
        "similarCorps": [
            {
                "corpId": "CP00000016",
                "bizNameEn": "콘텐츠/예술",
                "bizNameKr": "콘텐츠/예술",
                "corpNameEn": "RIDI CORPORATION",
                "corpNameKr": "리디",
                "prodNameEn": "",
                "prodNameKr": "리디",
                "corpIntroEn": "A company that operates a webtoon and web novel content platform [RIDI], etc.",
                "corpIntroKr": "웹툰·웹소설 콘텐츠 플랫폼 '리디' 등을 운영하는 기업",
                "corpLogoImg": "https://s3.ap-northeast-2.amazonaws.com/inno.bucket.live/corp/logo/C000064.png"
            }
        ],
        "customerSales": {
            "salesBasic": [
                {
                    "rate": 55.8,
                    "count": 58687,
                    "unitPrice": 13531.6,
                    "referenceMonth": "2022-02"
                },
                {
                    "rate": 55.1,
                    "count": 59233,
                    "unitPrice": 13235.4,
                    "referenceMonth": "2022-03"
                }
            ],
            "salesPeriod": [
                {
                    "period": "1개월내",
                    "repurchaseRate": 71.3,
                    "avgPurchaseRate": 1.0
                },
                {
                    "period": "3개월내",
                    "repurchaseRate": 72.5,
                    "avgPurchaseRate": 2.7
                }
            ],
            "recentUpdate": "2025-02-24"
        },
        "dataSufficient": True,
        "base_company_info": {
            "data": {
                "seedCorp": {
                    "id": "CP00001521",
                    "city": 11440,
                    "corpCd": "STARTUP",
                    "comment": None,
                    "cordLat": 126.913948,
                    "cordLng": 37.551502,
                    "foundAt": "2016-07-07",
                    "homeUrl": "www.millie.co.kr",
                    "subCorp": False,
                    "createBy": "system",
                    "invstCnt": 6,
                    "province": "SEOUL",
                    "showFlag": True,
                    "bizInfoEn": "Commercials Advertising Motion Picture and Video Production",
                    "bizInfoKr": "그외 기타 분류안된 사업지원 서비스업",
                    "corpAddrEn": "undefined",
                    "corpAddrKr": "서울 마포구 양화로 45 (서교동, 메세나폴리스) 16층",
                    "corpNameEn": "MILLY'S LIBRARY CO.,LTD.",
                    "corpNameKr": "밀리의서재",
                    "corpStatCd": "IN_OPERATION",
                    "createDate": "2021-05-28T11:15:16",
                    "hasSubCorp": False,
                    "investMemo": None,
                    "modifiedBy": "SYSTEM",
                    "capStockVal": "4194144000",
                    "corpIntroEn": "A company that operates the e-book subscription platform [MILLIE]",
                    "corpIntroKr": "전자책 정기구독 플랫폼 '밀리의 서재'를 운영하는 기업",
                    "corpLogoImg": "https://s3.ap-northeast-2.amazonaws.com/inno.bucket.live/corp/logo/C000095.png",
                    "empWholeVal": 188,
                    "invstSumVal": 62650000000,
                    "lastInvstAt": "2023-09-27",
                    "listingDate": "2023-09-27",
                    "patntLvlVal": 2.0,
                    "upperCorpId": None,
                    "corpStatCdEn": "운영중",
                    "corpStatCdKr": "운영중",
                    "emplWholeVal": 73,
                    "modifiedDate": "2025-02-24T19:30:08",
                    "corpStockCdEn": "KOSDAQ",
                    "corpStockCdKr": "KOSDAQ",
                    "logoImageFile": None,
                    "finacRevenueAt": "2023-12-31",
                    "niceCorpStatCd": "",
                    "finacRevenueVal": 56572749000,
                    "invstSumValText": "626.5억원",
                    "requestSendTypeCd": None,
                    "investmentDescription": ""
                },
                "seedBadge": [
                    {
                        "id": "BG00000060",
                        "badge": "혁신아이콘",
                        "endAt": "2030-01-01T16:55:10",
                        "comment": None,
                        "startAt": "2024-10-23T16:55:10",
                        "createBy": "wjy",
                        "showCode": "SHOWING",
                        "badgeImage": "https://s3.ap-northeast-2.amazonaws.com/inno.bucket.live/badge/logo/badge_20241023170730.png",
                        "bubbleText": "<p>혁신아이콘 설명</p>",
                        "createDate": "2024-10-23T17:07:31",
                        "modifiedBy": "jhmin",
                        "bubbleTitle": "<p>혁신아이콘</p>",
                        "modifiedDate": "2024-12-12T17:20:47",
                        "logoImageFile": None,
                        "bubbleButtonUrl": "https://www.innoforest.co.kr",
                        "bubbleButtonFlag": True,
                        "bubbleButtonText": "혁신아이콘 선정기업 보러가기",
                        "seedBadgeCorpCaches": None
                    }
                ],
                "seedPeople": [
                    {
                        "id": "PP00066846",
                        "fbUrl": "",
                        "corpId": "CP00001521",
                        "etcUrl": None,
                        "comment": None,
                        "ivstrId": None,
                        "useFlag": True,
                        "createBy": None,
                        "linkdUrl": "",
                        "showFlag": True,
                        "pplNameEn": "",
                        "pplNameKr": "박현진",
                        "pplRoleCd": "CEO",
                        "rocketUrl": "",
                        "corpNameEn": None,
                        "corpNameKr": None,
                        "createDate": None,
                        "crewRoleCd": None,
                        "hasHistory": None,
                        "modifiedBy": None,
                        "modifiedDate": None,
                        "seedPeopleHistories": None
                    }
                ],
                "seedCorpBiz": [
                    {
                        "biz": 3,
                        "corpCnt": 1396,
                        "createBy": "hskim",
                        "bizNameEn": "콘텐츠/예술",
                        "bizNameKr": "콘텐츠/예술",
                        "createDate": "2023-09-27T15:48:36"
                    }
                ],
                "seedCorpTag": [
                    {
                        "tag": "TG00000221",
                        "corpCnt": 133,
                        "tagNameEn": "webtoon/comics",
                        "tagNameKr": "웹툰/만화"
                    },
                    {
                        "tag": "TG00000229",
                        "corpCnt": 37,
                        "tagNameEn": "OTT",
                        "tagNameKr": "OTT"
                    },
                    {
                        "tag": "TG00030003",
                        "corpCnt": 383,
                        "tagNameEn": "Subscription",
                        "tagNameKr": "구독"
                    }
                ],
                "seedProduct": {
                    "id": "PD00000221",
                    "andUrl": "https://play.google.com/store/apps/details?id=kr.co.millie.millieshelf&hl=ko",
                    "corpId": "CP00001521",
                    "webUrl": "millie.co.kr",
                    "createBy": "system",
                    "isAppProd": False,
                    "isEtcProd": False,
                    "isOffProd": False,
                    "isWebProd": False,
                    "prodEndAt": None,
                    "createDate": "2021-09-16T00:00:00",
                    "finishFlag": False,
                    "modifiedBy": None,
                    "prodNameEn": "밀리의서재",
                    "prodNameKr": "밀리의서재",
                    "prodIntroEn": "독서와 무제한 친해지리, 밀리의 서재",
                    "prodIntroKr": "독서와 무제한 친해지리, 밀리의 서재",
                    "prodLogoImg": "https://lh3.googleusercontent.com/ck3EZc2bX63rxRC-aMdx46T-KcZiFtm8QxLLY81Yi8ej3mHv7xdBNWe_eT55s1Usa8AI",
                    "etcProdCount": None,
                    "modifiedDate": None,
                    "offProdCount": None
                },
                "seedPeopleBlind": False,
                "seedPeopleCount": 1,
                "seedCorpBizBlind": False,
                "seedCorpBizCount": 1,
                "seedCorpTagBlind": False,
                "seedCorpTagCount": 10,
                "seedProductBlind": False,
                "seedAdvertisementKeywords": [
                    {
                        "id": "AK00000054",
                        "corpCnt": 56,
                        "advertisementKeyword": "혁신아이콘"
                    }
                ]
            },
            "referrer": "",
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/122.0.6261.62 Mobile/15E148 Safari/604.1",
            "ogTagContent": {
                "title": "밀리의서재 - 매출 투자 고용 정보 - 혁신의숲",
                "thumbnail": "https://s3.ap-northeast-2.amazonaws.com/inno.bucket.live/corp/logo/C000095.png",
                "description": "누적투자금 626.5억 스타트업 밀리의서재의 매출, 투자, 고용, 특허등급, 재구매율, 방문자 분석 등 36개월 간의 데이터를 혁신의숲에서 확인해 보세요."
            }
        }
    }


@pytest.fixture  
def minimal_forest_of_hyuksin_data():
    """Minimal valid Forest of Hyuksin data structure for basic tests"""
    return {
        "mau": {
            "list": [],
            "recentUpdate": "2025-02-25"
        },
        "patent": {
            "list": [],
            "chart": [],
            "words": [],
            "totalCount": 0,
            "averageRank": 0.0,
            "recentUpdate": "2025-02-25"
        },
        "finance": {
            "data": [],
            "recentUpdate": "2025-02-25"
        },
        "products": [],
        "investment": {
            "data": [],
            "recentUpdate": "2025-02-25",
            "lastInvestmentLevel": "",
            "investmentDescription": "",
            "totalInvestmentAmount": 0
        },
        "customerType": {
            "salesFamily": [],
            "salesIncome": [],
            "salesPerson": [],
            "recentUpdate": "2025-02-25"
        },
        "organization": {
            "data": [],
            "retireRate": 0.0,
            "recentUpdate": "2025-02-25"
        },
        "similarCorps": [],
        "customerSales": {
            "salesBasic": [],
            "salesPeriod": [],
            "recentUpdate": "2025-02-25"
        },
        "dataSufficient": False,
        "base_company_info": {
            "data": {
                "seedCorp": {
                    "id": "CP00001521",
                    "city": 11440,
                    "corpCd": "STARTUP",
                    "comment": None,
                    "cordLat": 126.913948,
                    "cordLng": 37.551502,
                    "foundAt": "2016-07-07",
                    "homeUrl": "www.millie.co.kr",
                    "subCorp": False,
                    "createBy": "system",
                    "invstCnt": 0,
                    "province": "SEOUL",
                    "showFlag": True,
                    "bizInfoEn": "Test Business",
                    "bizInfoKr": "테스트 사업",
                    "corpAddrEn": "Test Address",
                    "corpAddrKr": "테스트 주소",
                    "corpNameEn": "Test Corp",
                    "corpNameKr": "테스트회사",
                    "corpStatCd": "IN_OPERATION",
                    "createDate": "2021-05-28T11:15:16",
                    "hasSubCorp": False,
                    "investMemo": None,
                    "modifiedBy": "SYSTEM",
                    "capStockVal": "1000000000",
                    "corpIntroEn": "Test company description",
                    "corpIntroKr": "테스트 회사 설명",
                    "corpLogoImg": "https://test.com/logo.png",
                    "empWholeVal": 50,
                    "invstSumVal": 0,
                    "lastInvstAt": None,
                    "listingDate": None,
                    "patntLvlVal": 0.0,
                    "upperCorpId": None,
                    "corpStatCdEn": "운영중",
                    "corpStatCdKr": "운영중",
                    "emplWholeVal": 25,
                    "modifiedDate": "2025-02-24T19:30:08",
                    "corpStockCdEn": "PRIVATE",
                    "corpStockCdKr": "비상장",
                    "logoImageFile": None,
                    "finacRevenueAt": "2023-12-31",
                    "niceCorpStatCd": "",
                    "finacRevenueVal": 0,
                    "invstSumValText": "0원",
                    "requestSendTypeCd": None,
                    "investmentDescription": ""
                },
                "seedBadge": [],
                "seedPeople": [
                    {
                        "id": "PP00000001",
                        "fbUrl": "",
                        "corpId": "CP00001521",
                        "etcUrl": None,
                        "comment": None,
                        "ivstrId": None,
                        "useFlag": True,
                        "createBy": None,
                        "linkdUrl": "",
                        "showFlag": True,
                        "pplNameEn": "Test CEO",
                        "pplNameKr": "테스트대표",
                        "pplRoleCd": "CEO",
                        "rocketUrl": "",
                        "corpNameEn": None,
                        "corpNameKr": None,
                        "createDate": None,
                        "crewRoleCd": None,
                        "hasHistory": None,
                        "modifiedBy": None,
                        "modifiedDate": None,
                        "seedPeopleHistories": None
                    }
                ],
                "seedCorpBiz": [
                    {
                        "biz": 1,
                        "corpCnt": 100,
                        "createBy": "system",
                        "bizNameEn": "Technology",
                        "bizNameKr": "기술",
                        "createDate": "2021-01-01T00:00:00"
                    }
                ],
                "seedCorpTag": [
                    {
                        "tag": "TG00000001",
                        "corpCnt": 50,
                        "tagNameEn": "startup",
                        "tagNameKr": "스타트업"
                    }
                ],
                "seedProduct": {
                    "id": "PD00000001",
                    "andUrl": "https://play.google.com/test",
                    "corpId": "CP00001521",
                    "webUrl": "test.com",
                    "createBy": "system",
                    "isAppProd": False,
                    "isEtcProd": False,
                    "isOffProd": False,
                    "isWebProd": False,
                    "prodEndAt": None,
                    "createDate": "2021-01-01T00:00:00",
                    "finishFlag": False,
                    "modifiedBy": None,
                    "prodNameEn": "Test Product",
                    "prodNameKr": "테스트제품",
                    "prodIntroEn": "Test product description",
                    "prodIntroKr": "테스트 제품 설명",
                    "prodLogoImg": "https://test.com/product-logo.png",
                    "etcProdCount": None,
                    "modifiedDate": None,
                    "offProdCount": None
                },
                "seedPeopleBlind": False,
                "seedPeopleCount": 1,
                "seedCorpBizBlind": False,
                "seedCorpBizCount": 1,
                "seedCorpTagBlind": False,
                "seedCorpTagCount": 1,
                "seedProductBlind": False,
                "seedAdvertisementKeywords": []
            },
            "referrer": "",
            "userAgent": "Mozilla/5.0 (test)",
            "ogTagContent": {
                "title": "테스트 회사",
                "thumbnail": "https://test.com/logo.png",
                "description": "테스트용 회사 설명"
            }
        }
    }


@pytest.fixture
def sample_company_id():
    """Sample company UUID"""
    return UUID("12345678-1234-5678-9abc-123456789012")


@pytest.fixture
def sample_company(sample_company_id):
    """Sample Company entity for testing"""
    return Company(
        id=sample_company_id,
        external_id="CP00001521",
        name="밀리의서재",
        name_en="MILLY'S LIBRARY CO.,LTD.",
        industry=["콘텐츠/예술"],
        tags=["웹툰/만화", "OTT", "구독"],
        founded_date=date(2016, 7, 7),
        employee_count=73,
        stage="IPO",
        business_description="전자책 정기구독 플랫폼 '밀리의 서재'를 운영하는 기업",
        ipo_date=date(2023, 9, 27),
        total_investment=62650000000,
        origin_file_path="/test/data/millie.json"
    )


@pytest.fixture
def sample_company_aliases(sample_company_id):
    """Sample CompanyAlias entities"""
    return [
        CompanyAlias(
            company_id=sample_company_id,
            alias="밀리의서재",
            alias_type="name",
            id=1
        ),
        CompanyAlias(
            company_id=sample_company_id,
            alias="MILLY'S LIBRARY CO.,LTD.",
            alias_type="name",
            id=2
        )
    ]


@pytest.fixture
def sample_company_metrics_snapshots(sample_company_id):
    """Sample CompanyMetricsSnapshot entities"""
    return [
        CompanyMetricsSnapshot(
            company_id=sample_company_id,
            reference_date=date(2022, 3, 1),
            metrics=MonthlyMetrics(
                mau=[],
                patents=[],
                finance=[],
                investments=[],
                organizations=[]
            ),
            id=1
        )
    ]


@pytest.fixture
def sample_company_aggregate(sample_company, sample_company_aliases, sample_company_metrics_snapshots):
    """Sample CompanyAggregate"""
    return CompanyAggregate(
        company=sample_company,
        company_aliases=sample_company_aliases,
        company_metrics_snapshots=sample_company_metrics_snapshots
    )