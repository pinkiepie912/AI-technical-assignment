import pytest

@pytest.fixture
def company_data_fixture():
    return {
        "mau": {
            "list": [
                {
                    "data": [
                        {
                            "value": 17420016,
                            "growthRate": None,
                            "referenceMonth": "2022-03"
                        },
                        {
                            "value": 17345672,
                            "growthRate": -0.4,
                            "referenceMonth": "2022-04"
                        }
                    ],
                    "manual": False,
                    "productId": "PD00003805"
                },
                {
                    "data": [
                        {
                            "value": 80394,
                            "growthRate": None,
                            "referenceMonth": "2022-03"
                        },
                        {
                            "value": 82340,
                            "growthRate": 2.4,
                            "referenceMonth": "2022-04"
                        }
                    ],
                    "manual": False,
                    "productId": "PD00012733"
                }
            ],
            "recentUpdate": "2025-02-25"
        },
        "patent": {
            "list": [
                {
                    "level": "B0",
                    "title": "유저정보 스크래핑 방법 및 이를 위한 애플리케이션 시스템",
                    "registerAt": "2017-08-31"
                },
                {
                    "level": "B0",
                    "title": "전자적 정보와 실제 자금을 분리하여 처리하는 금융 서비스 방법 및 시스템",
                    "registerAt": "2014-05-15"
                }
            ],
            "chart": [
                {
                    "count": 2,
                    "level": "B0"
                },
                {
                    "count": 5,
                    "level": "B-"
                }
            ],
            "words": [
                {
                    "text": "유저",
                    "patentCount": 8,
                    "displayCount": 53
                },
                {
                    "text": "스크래핑",
                    "patentCount": 5,
                    "displayCount": 36
                }
            ],
            "totalCount": 9,
            "averageRank": 3.0,
            "recentUpdate": "2022-01-25"
        },
        "finance": {
            "data": [
                {
                    "type": "CONSOLIDATED_NICE",
                    "year": 2021,
                    "profit": 780756856000,
                    "capital": 32651671000,
                    "netProfit": -215363708000,
                    "liabilities": 1301064490000,
                    "totalAssets": 2025822087000,
                    "totalCapital": 724757597000,
                    "operatingProfit": -179627580000
                },
                {
                    "type": "CONSOLIDATED_NICE",
                    "year": 2022,
                    "profit": 1188787782000,
                    "capital": 35060231000,
                    "netProfit": -322251301000,
                    "liabilities": 1865174894000,
                    "totalAssets": 2737618487000,
                    "totalCapital": 872443593000,
                    "operatingProfit": -247201063000
                }
            ],
            "recentUpdate": "2025-02-25"
        },
        "products": [
            {
                "id": "PD00003805",
                "name": "토스",
                "types": [
                    {
                        "url": "https://play.google.com/store/apps/details?id=viva.republica.toss",
                        "type": "APP"
                    },
                    {
                        "url": "toss.im",
                        "type": "WEB"
                    }
                ],
                "finishedAt": None,
                "logoImgUrl": "https://s3.ap-northeast-2.amazonaws.com/inno.bucket.live/product/logo/PD00003805_20231211102512.png"
            },
            {
                "id": "PD00012733",
                "name": "토스보험파트너",
                "types": [
                    {
                        "url": "https://play.google.com/store/apps/details?id=im.toss.app.insurp",
                        "type": "APP"
                    }
                ],
                "finishedAt": None,
                "logoImgUrl": "https://s3.ap-northeast-2.amazonaws.com/inno.bucket.live/product/logo/PD00012733_20230313144902.png"
            }
        ],
        "investment": {
            "data": [
                {
                    "level": "series G",
                    "investAt": "2022-08-25",
                    "investor": [
                        {
                            "id": "IV00002476",
                            "name": "토닉프라이빗에쿼티",
                            "hasLink": False
                        },
                        {
                            "id": "IV99999999",
                            "name": "비공개투자자",
                            "hasLink": False
                        }
                    ],
                    "investmentAmount": 230000000000
                },
                {
                    "level": "series G",
                    "investAt": "2022-07-21",
                    "investor": [
                        {
                            "id": "IV00001012",
                            "name": "알토스벤처스",
                            "hasLink": True
                        },
                        {
                            "id": "IV00000065",
                            "name": "굿워터캐피털",
                            "hasLink": True
                        }
                    ],
                    "investmentAmount": 300000000000
                }
            ],
            "recentUpdate": "2023-07-12",
            "lastInvestmentLevel": "series G",
            "investmentDescription": "",
            "totalInvestmentAmount": 1493900000000
        },
        "customerType": {
            "salesFamily": [
                {
                    "rate": 8.3,
                    "type": "성인자녀가구"
                },
                {
                    "rate": 10.7,
                    "type": "유아자녀가구"
                }
            ],
            "salesIncome": [
                {
                    "rate": 2.6,
                    "type": "2000만원이하"
                },
                {
                    "rate": 14.4,
                    "type": "3000만원이하"
                }
            ],
            "salesPerson": [
                {
                    "rate": 17.1,
                    "gender": "여성",
                    "ageGroup": "40~49세"
                },
                {
                    "rate": 8.3,
                    "gender": "여성",
                    "ageGroup": "50~59세"
                }
            ],
            "recentUpdate": "2025-02-24"
        },
        "organization": {
            "data": [
                {
                    "in": 66,
                    "out": 23,
                    "value": 1105,
                    "growRate": 3.7,
                    "referenceMonth": "2025-01"
                },
                {
                    "in": 44,
                    "out": 27,
                    "value": 1066,
                    "growRate": 0.9,
                    "referenceMonth": "2024-12"
                }
            ],
            "retireRate": 34.3,
            "recentUpdate": "2025-02-24"
        },
        "similarCorps": [
            {
                "corpId": "CP00003068",
                "bizNameEn": "금융/보험/핀테크",
                "bizNameKr": "금융/보험/핀테크",
                "corpNameEn": "Kakaopay Corp.",
                "corpNameKr": "카카오페이",
                "prodNameEn": "카카오페이",
                "prodNameKr": "카카오페이",
                "corpIntroEn": "A company that operates the online payment service [KAKAO PAY]",
                "corpIntroKr": "온라인 결제 서비스 '카카오페이'를 운영하는 기업",
                "corpLogoImg": "https://s3.ap-northeast-2.amazonaws.com/inno.bucket.live/corp/logo/data_20210323140616.png"
            },
            {
                "corpId": "CP00003321",
                "bizNameEn": "커머스,금융/보험/핀테크",
                "bizNameKr": "커머스,금융/보험/핀테크",
                "corpNameEn": "Coupang Pay, Ltd.",
                "corpNameKr": "쿠팡페이",
                "prodNameEn": "coupay",
                "prodNameKr": "쿠페이",
                "corpIntroEn": "A company that provides online payment service [COUPAY]",
                "corpIntroKr": "온라인 결제 서비스 '쿠페이'를 제공하는 기업",
                "corpLogoImg": "https://s3.ap-northeast-2.amazonaws.com/inno.bucket.live/corp/logo/data_20210616103000.png"
            }
        ],
        "customerSales": {
            "salesBasic": [
                {
                    "rate": 10.5,
                    "count": 309728,
                    "unitPrice": 31806.3,
                    "referenceMonth": "2022-02"
                },
                {
                    "rate": 9.8,
                    "count": 319624,
                    "unitPrice": 28571.1,
                    "referenceMonth": "2022-03"
                }
            ],
            "salesPeriod": [
                {
                    "period": "1개월",
                    "repurchaseRate": 0.5,
                    "avgPurchaseRate": 1.2
                },
                {
                    "period": "2개월",
                    "repurchaseRate": 0.3,
                    "avgPurchaseRate": 1.1
                }
            ],
            "recentUpdate": "2025-02-24"
        },
        "dataSufficient": True,
        "base_company_info": {
            "data": {
                "seedCorp": {
                    "id": "CP00001709",
                    "city": 1,
                    "corpCd": "1101115316385",
                    "comment": None,
                    "cordLat": 37.494334,
                    "cordLng": 127.030232,
                    "foundAt": "2013-08-01",
                    "homeUrl": "toss.im",
                    "subCorp": False,
                    "createBy": "U00000001",
                    "invstCnt": 12,
                    "province": "서울",
                    "showFlag": True,
                    "bizInfoEn": "",
                    "bizInfoKr": "금융/보험/핀테크",
                    "corpAddrEn": "",
                    "corpAddrKr": "서울특별시 강남구 테헤란로 142, 12층 (역삼동, 아크플레이스)",
                    "corpNameEn": "Viva Republica Inc.",
                    "corpNameKr": "비바리퍼블리카",
                    "corpStatCd": "운영",
                    "createDate": "2019-01-01T00:00:00",
                    "hasSubCorp": False,
                    "investMemo": None,
                    "modifiedBy": "U00000001",
                    "capStockVal": "35237098000",
                    "corpIntroEn": "A company that operates the simple remittance service [TOSS]",
                    "corpIntroKr": "간편 송금 서비스 '토스'를 운영하는 기업",
                    "corpLogoImg": "https://s3.ap-northeast-2.amazonaws.com/inno.bucket.live/corp/logo/CP00001709_20231211102512.png",
                    "empWholeVal": 1105,
                    "invstSumVal": 1493900000000,
                    "lastInvstAt": "2022-08-25",
                    "listingDate": None,
                    "patntLvlVal": 3.0,
                    "upperCorpId": None,
                    "corpStatCdEn": "In Operation",
                    "corpStatCdKr": "운영",
                    "emplWholeVal": 1105,
                    "modifiedDate": "2024-01-01T00:00:00",
                    "corpStockCdEn": "",
                    "corpStockCdKr": "",
                    "logoImageFile": None,
                    "finacRevenueAt": "2023",
                    "niceCorpStatCd": "정상",
                    "finacRevenueVal": 336172174000,
                    "invstSumValText": "1조 4939억",
                    "requestSendTypeCd": None,
                    "investmentDescription": ""
                },
                "seedBadge": [],
                "seedPeople": [],
                "seedCorpBiz": [],
                "seedCorpTag": [],
                "seedProduct": {},
                "seedPeopleBlind": False,
                "seedPeopleCount": 0,
                "seedCorpBizBlind": False,
                "seedCorpBizCount": 0,
                "seedCorpTagBlind": False,
                "seedCorpTagCount": 0,
                "seedProductBlind": False,
                "seedAdvertisementKeywords": []
            },
            "referrer": "",
            "userAgent": "",
            "ogTagContent": {
                "title": "비바리퍼블리카(토스) 기업정보 - ZUZU",
                "thumbnail": "https://inno-prod.s3.ap-northeast-2.amazonaws.com/og/corp/CP00001709_16871814.png",
                "description": "누적투자금 1.5조 스타트업 비바리퍼블리카(토스)의 매출, 투자, 고용, 특허등급, 재구매율, 방문자 분석 등 36개월 간의 데이터를 혁신의숲에서 확인해 보세요."
            }
        }
    }
