import json
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest


class ReaderTestDatasets:
    @staticmethod
    def get_complete_forest_of_hyuksin_data() -> Dict[str, Any]:
        return {
            "mau": {
                "list": [
                    {
                        "data": [
                            {
                                "value": 1500000,
                                "growthRate": 12.5,
                                "referenceMonth": "2024-01",
                            },
                            {
                                "value": 1680000,
                                "growthRate": 12.0,
                                "referenceMonth": "2024-02",
                            },
                        ],
                        "manual": False,
                        "productId": "test_product_main",
                    },
                    {
                        "data": [
                            {
                                "value": 850000,
                                "growthRate": 8.3,
                                "referenceMonth": "2024-01",
                            }
                        ],
                        "manual": True,
                        "productId": "test_product_secondary",
                    },
                ],
                "recentUpdate": "2024-02-15",
            },
            "patent": {
                "list": [
                    {
                        "level": "HIGH",
                        "title": "혁신적인 데이터 처리 방법",
                        "registerAt": "2023-05-15",
                    },
                    {
                        "level": "MEDIUM",
                        "title": "효율적인 검색 알고리즘",
                        "registerAt": "2023-08-22",
                    },
                ],
                "chart": [
                    {"count": 15, "level": "HIGH"},
                    {"count": 8, "level": "MEDIUM"},
                    {"count": 3, "level": "LOW"},
                ],
                "words": [
                    {"text": "인공지능", "patentCount": 12, "displayCount": 12},
                    {"text": "머신러닝", "patentCount": 8, "displayCount": 8},
                    {"text": "데이터", "patentCount": 26, "displayCount": 20},
                ],
                "totalCount": 26,
                "averageRank": 4.2,
                "recentUpdate": "2024-02-10",
            },
            "finance": {
                "data": [
                    {
                        "type": "annual",
                        "year": 2023,
                        "profit": 5000000000,
                        "capital": 2000000000,
                        "netProfit": 4200000000,
                        "liabilities": 800000000,
                        "totalAssets": 6800000000,
                        "totalCapital": 6000000000,
                        "operatingProfit": 4500000000,
                    },
                    {
                        "type": "annual",
                        "year": 2022,
                        "profit": 4200000000,
                        "capital": 1800000000,
                        "netProfit": 3500000000,
                        "liabilities": 700000000,
                        "totalAssets": 5800000000,
                        "totalCapital": 5100000000,
                        "operatingProfit": 3800000000,
                    },
                ],
                "recentUpdate": "2024-01-31",
            },
            "products": [
                {
                    "id": "prod_main",
                    "name": "테스트 메인 서비스",
                    "types": [
                        {"url": "https://testcorp.com", "type": "WEB"},
                        {
                            "url": "https://play.google.com/store/apps/details?id=com.testcorp.main",
                            "type": "APP",
                        },
                        {"url": None, "type": "IOS"},
                    ],
                    "finishedAt": None,
                    "logoImgUrl": "https://testcorp.com/assets/main_logo.png",
                },
                {
                    "id": "prod_sub",
                    "name": "테스트 서브 서비스",
                    "types": [{"url": "https://sub.testcorp.com", "type": "WEB"}],
                    "finishedAt": "2023-12-31",
                    "logoImgUrl": "https://testcorp.com/assets/sub_logo.png",
                },
            ],
            "customerType": {
                "salesFamily": [
                    {"rate": 45.2, "type": "1인 가구"},
                    {"rate": 32.8, "type": "2인 가구"},
                    {"rate": 22.0, "type": "3인 이상 가구"},
                ],
                "salesIncome": [
                    {"rate": 28.5, "type": "3천만원 이하"},
                    {"rate": 35.2, "type": "3천만원-5천만원"},
                    {"rate": 24.8, "type": "5천만원-7천만원"},
                    {"rate": 11.5, "type": "7천만원 이상"},
                ],
                "salesPerson": [
                    {"rate": 52.3, "gender": "여성", "ageGroup": "20대"},
                    {"rate": 31.7, "gender": "남성", "ageGroup": "30대"},
                    {"rate": 16.0, "gender": "여성", "ageGroup": "40대"},
                ],
                "recentUpdate": "2024-02-01",
            },
            "organization": {
                "data": [
                    {
                        "in": 25,
                        "out": 8,
                        "value": 150,
                        "growRate": 15.2,
                        "referenceMonth": "2024-01",
                    },
                    {
                        "in": 18,
                        "out": 12,
                        "value": 156,
                        "growRate": 4.0,
                        "referenceMonth": "2024-02",
                    },
                ],
                "retireRate": 12.8,
                "recentUpdate": "2024-02-15",
            },
            "similarCorps": [
                {
                    "corpId": "similar_001",
                    "bizNameEn": "Similar Tech Solutions",
                    "bizNameKr": "유사 기술 솔루션",
                    "corpNameEn": "SimilarTech Corp",
                    "corpNameKr": "유사테크 코퍼레이션",
                    "prodNameEn": "SimilarTech Platform",
                    "prodNameKr": "유사테크 플랫폼",
                    "corpIntroEn": "Leading technology solutions provider",
                    "corpIntroKr": "선도적인 기술 솔루션 제공업체",
                    "corpLogoImg": "https://similartech.com/logo.png",
                }
            ],
            "customerSales": {
                "salesBasic": [
                    {
                        "rate": 15.8,
                        "count": 12500,
                        "unitPrice": 35000.0,
                        "referenceMonth": "2024-01",
                    },
                    {
                        "rate": 18.2,
                        "count": 14800,
                        "unitPrice": 36500.0,
                        "referenceMonth": "2024-02",
                    },
                ],
                "salesPeriod": [
                    {"period": "1개월", "repurchaseRate": 75.5, "avgPurchaseRate": 2.3},
                    {"period": "3개월", "repurchaseRate": 65.2, "avgPurchaseRate": 1.8},
                ],
                "recentUpdate": "2024-02-15",
            },
            "investment": {
                "data": [
                    {
                        "round": "Series A",
                        "amount": 5000000000,
                        "date": "2023-03-15",
                        "investors": ["벤처캐피탈A", "엔젤투자자B"],
                    }
                ],
                "recentUpdate": "2024-01-15",
                "totalInvestmentAmount": 5000000000,
                "lastInvestmentLevel": "Series A",
                "investmentDescription": "AI 기술 개발 및 시장 확장을 위한 투자",
            },
            "dataSufficient": True,
            "base_company_info": {
                "data": {
                    "seedCorp": {
                        "id": "testcorp_001",
                        "city": 1,
                        "corpCd": "TC001",
                        "comment": None,
                        "cordLat": 37.5665,
                        "cordLng": 126.9780,
                        "foundAt": "2020-03-15",
                        "homeUrl": "https://testcorp.com",
                        "subCorp": False,
                        "createBy": "system",
                        "invstCnt": 1,
                        "province": "서울특별시",
                        "showFlag": True,
                        "bizInfoEn": "AI-powered data solutions",
                        "bizInfoKr": "AI 기반 데이터 솔루션",
                        "corpAddrEn": "123 Teheran-ro, Gangnam-gu, Seoul",
                        "corpAddrKr": "서울특별시 강남구 테헤란로 123",
                        "corpNameEn": "TestCorp Inc.",
                        "corpNameKr": "테스트코프 주식회사",
                        "corpStatCd": "ACTIVE",
                        "createDate": "2020-03-15",
                        "hasSubCorp": False,
                        "investMemo": None,
                        "modifiedBy": "admin",
                        "capStockVal": "10000000000",
                        "corpIntroEn": "Leading AI technology company specializing in data processing solutions",
                        "corpIntroKr": "데이터 처리 솔루션 전문 AI 기술 선도 기업",
                        "corpLogoImg": "https://testcorp.com/assets/logo.png",
                        "empWholeVal": 156,
                        "invstSumVal": 5000000000,
                        "lastInvstAt": "2023-03-15",
                        "listingDate": None,
                        "patntLvlVal": 4.2,
                        "upperCorpId": None,
                        "corpStatCdEn": "Active",
                        "corpStatCdKr": "활성",
                        "emplWholeVal": 156,
                        "modifiedDate": "2024-02-01",
                        "corpStockCdEn": "UNLISTED",
                        "corpStockCdKr": "비상장",
                        "logoImageFile": None,
                        "finacRevenueAt": "2023-12-31",
                        "niceCorpStatCd": "NORMAL",
                        "finacRevenueVal": 5000000000,
                        "invstSumValText": "50억원",
                        "requestSendTypeCd": None,
                        "investmentDescription": "AI 기술 개발 투자",
                    },
                    "seedBadge": [
                        {
                            "id": "badge_001",
                            "badge": "AI_LEADER",
                            "endAt": "2024-12-31",
                            "comment": None,
                            "startAt": "2024-01-01",
                            "createBy": "system",
                            "showCode": "SHOW",
                            "badgeImage": "https://badges.testcorp.com/ai_leader.png",
                            "bubbleText": "AI 분야 선도기업",
                            "createDate": "2024-01-01",
                            "modifiedBy": "admin",
                            "bubbleTitle": "AI 리더",
                            "modifiedDate": "2024-01-15",
                            "logoImageFile": None,
                            "bubbleButtonUrl": "https://testcorp.com/ai-solutions",
                            "bubbleButtonFlag": True,
                            "bubbleButtonText": "솔루션 보기",
                            "seedBadgeCorpCaches": None,
                        }
                    ],
                    "seedPeople": [
                        {
                            "id": "people_001",
                            "fbUrl": "https://facebook.com/testceo",
                            "corpId": "testcorp_001",
                            "etcUrl": None,
                            "comment": None,
                            "ivstrId": None,
                            "useFlag": True,
                            "createBy": "system",
                            "linkdUrl": "https://linkedin.com/in/testceo",
                            "showFlag": True,
                            "pplNameEn": "John Kim",
                            "pplNameKr": "김테스트",
                            "pplRoleCd": "CEO",
                            "rocketUrl": None,
                            "corpNameEn": "TestCorp Inc.",
                            "corpNameKr": "테스트코프 주식회사",
                            "createDate": "2020-03-15",
                            "crewRoleCd": "FOUNDER",
                            "hasHistory": True,
                            "modifiedBy": "admin",
                            "modifiedDate": "2024-01-15",
                            "seedPeopleHistories": None,
                        }
                    ],
                    "seedCorpBiz": [
                        {
                            "biz": 1,
                            "corpCnt": 1,
                            "createBy": "system",
                            "bizNameEn": "Artificial Intelligence",
                            "bizNameKr": "인공지능",
                            "createDate": "2020-03-15",
                        },
                        {
                            "biz": 2,
                            "corpCnt": 1,
                            "createBy": "system",
                            "bizNameEn": "Data Processing",
                            "bizNameKr": "데이터 처리",
                            "createDate": "2020-03-15",
                        },
                    ],
                    "seedCorpTag": [
                        {
                            "tag": "AI",
                            "corpCnt": 1,
                            "tagNameEn": "Artificial Intelligence",
                            "tagNameKr": "인공지능",
                        },
                        {
                            "tag": "BIGDATA",
                            "corpCnt": 1,
                            "tagNameEn": "Big Data",
                            "tagNameKr": "빅데이터",
                        },
                    ],
                    "seedProduct": {
                        "id": "seedprod_001",
                        "andUrl": "https://play.google.com/store/apps/details?id=com.testcorp.main",
                        "corpId": "testcorp_001",
                        "webUrl": "https://testcorp.com",
                        "createBy": "system",
                        "isAppProd": True,
                        "isEtcProd": False,
                        "isOffProd": False,
                        "isWebProd": True,
                        "prodEndAt": None,
                        "createDate": "2020-03-15",
                        "finishFlag": False,
                        "modifiedBy": "admin",
                        "prodNameEn": "TestCorp AI Platform",
                        "prodNameKr": "테스트코프 AI 플랫폼",
                        "prodIntroEn": "Advanced AI-powered data processing platform",
                        "prodIntroKr": "고도화된 AI 기반 데이터 처리 플랫폼",
                        "prodLogoImg": "https://testcorp.com/assets/product_logo.png",
                        "etcProdCount": None,
                        "modifiedDate": "2024-02-01",
                        "offProdCount": None,
                    },
                    "seedPeopleBlind": False,
                    "seedPeopleCount": 1,
                    "seedCorpBizBlind": False,
                    "seedCorpBizCount": 2,
                    "seedCorpTagBlind": False,
                    "seedCorpTagCount": 2,
                    "seedProductBlind": False,
                    "seedAdvertisementKeywords": [
                        {
                            "id": "keyword_001",
                            "corpCnt": 1,
                            "advertisementKeyword": "AI 솔루션",
                        },
                        {
                            "id": "keyword_002",
                            "corpCnt": 1,
                            "advertisementKeyword": "데이터 분석",
                        },
                    ],
                },
                "referrer": "https://search.testcorp.com",
                "userAgent": "TestCorp-Bot/2.0",
                "ogTagContent": {
                    "title": "테스트코프 - AI 기반 데이터 솔루션",
                    "thumbnail": "https://testcorp.com/assets/og_image.jpg",
                    "description": "혁신적인 AI 기술로 데이터 처리의 새로운 패러다임을 제시하는 테스트코프입니다.",
                },
            },
        }

    @staticmethod
    def get_minimal_forest_of_hyuksin_data() -> Dict[str, Any]:
        return {
            "mau": {"list": [], "recentUpdate": "2024-01-15"},
            "finance": {"data": [], "recentUpdate": "2024-01-15"},
            "products": [],
            "organization": {
                "data": [],
                "retireRate": 0.0,
                "recentUpdate": "2024-01-15",
            },
            "similarCorps": [],
            "dataSufficient": False,
            "base_company_info": {
                "data": {
                    "seedCorp": {
                        "id": "minimal_001",
                        "city": 1,
                        "corpCd": "MIN001",
                        "comment": None,
                        "cordLat": None,
                        "cordLng": None,
                        "foundAt": "2020-01-01",
                        "homeUrl": "http://minimal.com",
                        "subCorp": False,
                        "createBy": "system",
                        "invstCnt": 0,
                        "province": "서울",
                        "showFlag": True,
                        "bizInfoEn": "Minimal Corp",
                        "bizInfoKr": "미니멀 코퍼레이션",
                        "corpAddrEn": "Seoul, Korea",
                        "corpAddrKr": "서울, 대한민국",
                        "corpNameEn": "Minimal Corp",
                        "corpNameKr": "미니멀 코퍼레이션",
                        "corpStatCd": "ACTIVE",
                        "createDate": "2020-01-01",
                        "hasSubCorp": False,
                        "investMemo": None,
                        "modifiedBy": "system",
                        "capStockVal": "100000000",
                        "corpIntroEn": "Minimal Corporation",
                        "corpIntroKr": "미니멀 코퍼레이션",
                        "corpLogoImg": "minimal.png",
                        "empWholeVal": 1,
                        "invstSumVal": None,
                        "lastInvstAt": None,
                        "listingDate": None,
                        "patntLvlVal": None,
                        "upperCorpId": None,
                        "corpStatCdEn": "Active",
                        "corpStatCdKr": "활성",
                        "emplWholeVal": None,
                        "modifiedDate": "2020-01-01",
                        "corpStockCdEn": "UNLISTED",
                        "corpStockCdKr": "비상장",
                        "logoImageFile": None,
                        "finacRevenueAt": "2020-12-31",
                        "niceCorpStatCd": "NORMAL",
                        "finacRevenueVal": 100000000,
                        "invstSumValText": "1억원",
                        "requestSendTypeCd": None,
                        "investmentDescription": "창업 투자",
                    },
                    "seedBadge": [],
                    "seedPeople": [],
                    "seedCorpBiz": [],
                    "seedCorpTag": [],
                    "seedProduct": {
                        "id": "minimal_prod",
                        "andUrl": None,
                        "corpId": "minimal_001",
                        "webUrl": "http://minimal.com",
                        "createBy": "system",
                        "isAppProd": False,
                        "isEtcProd": False,
                        "isOffProd": False,
                        "isWebProd": True,
                        "prodEndAt": None,
                        "createDate": "2020-01-01",
                        "finishFlag": False,
                        "modifiedBy": None,
                        "prodNameEn": "Minimal Product",
                        "prodNameKr": "미니멀 제품",
                        "prodIntroEn": "Minimal Product",
                        "prodIntroKr": "미니멀 제품",
                        "prodLogoImg": "minimal.png",
                        "etcProdCount": None,
                        "modifiedDate": None,
                        "offProdCount": None,
                    },
                    "seedPeopleBlind": False,
                    "seedPeopleCount": 0,
                    "seedCorpBizBlind": False,
                    "seedCorpBizCount": 0,
                    "seedCorpTagBlind": False,
                    "seedCorpTagCount": 0,
                    "seedProductBlind": False,
                    "seedAdvertisementKeywords": [],
                },
                "referrer": "minimal",
                "userAgent": "minimal",
                "ogTagContent": {
                    "title": "Minimal",
                    "thumbnail": "minimal.png",
                    "description": "Minimal",
                },
            },
        }

    @staticmethod
    def get_invalid_schema_data() -> Dict[str, Any]:
        return {
            "wrong_field": "invalid",
            "missing_required": True,
            "mau": {"wrong_structure": []},
        }

    @staticmethod
    def get_incomplete_required_fields_data() -> Dict[str, Any]:
        return {
            "mau": {"list": [], "recentUpdate": "2024-01-15"},
            "finance": {"data": [], "recentUpdate": "2024-01-15"},
            # Missing: products, organization, similarCorps, dataSufficient, base_company_info
        }


@pytest.fixture
def reader_datasets() -> ReaderTestDatasets:
    """Provide access to reader test datasets"""
    return ReaderTestDatasets()


@pytest.fixture
def complete_forest_data(reader_datasets: ReaderTestDatasets) -> Dict[str, Any]:
    """Complete Forest of Hyuksin test data with all fields populated"""
    return reader_datasets.get_complete_forest_of_hyuksin_data()


@pytest.fixture
def minimal_forest_data(reader_datasets: ReaderTestDatasets) -> Dict[str, Any]:
    """Minimal Forest of Hyuksin test data with only required fields"""
    return reader_datasets.get_minimal_forest_of_hyuksin_data()


@pytest.fixture
def invalid_schema_data(reader_datasets: ReaderTestDatasets) -> Dict[str, Any]:
    """Invalid schema data for error testing"""
    return reader_datasets.get_invalid_schema_data()


@pytest.fixture
def incomplete_data(reader_datasets: ReaderTestDatasets) -> Dict[str, Any]:
    """Incomplete data missing required fields"""
    return reader_datasets.get_incomplete_required_fields_data()


@pytest.fixture
def temp_json_file() -> Path:
    """Create a temporary JSON file - to be used with data from other fixtures"""

    def _create_file(data: Dict[str, Any]) -> Path:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            return Path(f.name)

    return _create_file


@pytest.fixture
def invalid_json_file() -> Path:
    """Create a temporary file with malformed JSON"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        f.write('{"malformed": json, "syntax": error}')
        return Path(f.name)


@pytest.fixture
def binary_file() -> Path:
    """Create a temporary binary file that cannot be decoded as UTF-8"""
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".json", delete=False) as f:
        # Write invalid UTF-8 bytes
        f.write(b"\xff\xfe\x00\x00\x84\x85invalid utf-8 content")
        return Path(f.name)

