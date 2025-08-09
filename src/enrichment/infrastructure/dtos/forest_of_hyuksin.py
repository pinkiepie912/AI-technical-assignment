from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["ForestOfHyuksinCompanyData"]


class _IgnoreExtraModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class MAUDataPoint(_IgnoreExtraModel):
    value: int
    growthRate: Optional[float]
    referenceMonth: str


class MAUProduct(_IgnoreExtraModel):
    data: List[MAUDataPoint]
    manual: bool
    productId: str


class MAUInfo(_IgnoreExtraModel):
    list: List[MAUProduct]
    recentUpdate: str


class PatentListItem(_IgnoreExtraModel):
    level: str
    title: str
    registerAt: str


class PatentChart(_IgnoreExtraModel):
    count: int
    level: str


class PatentWord(_IgnoreExtraModel):
    text: str
    patentCount: int
    displayCount: int


class PatentInfo(_IgnoreExtraModel):
    list: List[PatentListItem]
    chart: List[PatentChart]
    words: List[PatentWord]
    totalCount: int
    averageRank: float
    recentUpdate: str


class FinanceData(_IgnoreExtraModel):
    type: str
    year: int
    profit: int
    capital: int
    netProfit: Optional[int]
    liabilities: int
    totalAssets: int
    totalCapital: int
    operatingProfit: int


class FinanceInfo(_IgnoreExtraModel):
    data: List[FinanceData]
    recentUpdate: str


class ProductType(_IgnoreExtraModel):
    url: Optional[str] = None
    type: str


class Product(_IgnoreExtraModel):
    id: str
    name: str
    types: List[ProductType]
    finishedAt: Optional[str]
    logoImgUrl: str


class CustomerTypeItem(_IgnoreExtraModel):
    rate: float
    type: str


class CustomerPersonItem(_IgnoreExtraModel):
    rate: float
    gender: str
    ageGroup: str


class CustomerTypeInfo(_IgnoreExtraModel):
    salesFamily: List[CustomerTypeItem]
    salesIncome: List[CustomerTypeItem]
    salesPerson: List[CustomerPersonItem]
    recentUpdate: str


class OrganizationData(_IgnoreExtraModel):
    in_: int = Field(alias="in")
    out: int
    value: int
    growRate: float
    referenceMonth: str


class OrganizationInfo(_IgnoreExtraModel):
    data: List[OrganizationData]
    retireRate: float
    recentUpdate: str


class SimilarCorp(_IgnoreExtraModel):
    corpId: str
    bizNameEn: str
    bizNameKr: str
    corpNameEn: str
    corpNameKr: str
    prodNameEn: str
    prodNameKr: str
    corpIntroEn: str
    corpIntroKr: str
    corpLogoImg: str


class SalesBasic(_IgnoreExtraModel):
    rate: float
    count: int
    unitPrice: float
    referenceMonth: str


class SalesPeriod(_IgnoreExtraModel):
    period: str
    repurchaseRate: float
    avgPurchaseRate: float


class CustomerSalesInfo(_IgnoreExtraModel):
    salesBasic: List[SalesBasic]
    salesPeriod: List[SalesPeriod]
    recentUpdate: str


class SeedCorp(_IgnoreExtraModel):
    id: str
    city: int
    corpCd: str
    comment: Optional[str]
    cordLat: Optional[float]
    cordLng: Optional[float]
    foundAt: str
    homeUrl: str
    subCorp: bool
    createBy: str
    invstCnt: int
    province: str
    showFlag: bool
    bizInfoEn: str
    bizInfoKr: str
    corpAddrEn: str
    corpAddrKr: str
    corpNameEn: str
    corpNameKr: str
    corpStatCd: str
    createDate: str
    hasSubCorp: bool
    investMemo: Optional[str]
    modifiedBy: str
    capStockVal: str
    corpIntroEn: str
    corpIntroKr: str
    corpLogoImg: str
    empWholeVal: int
    invstSumVal: Optional[int]
    lastInvstAt: Optional[str]
    listingDate: Optional[str]
    patntLvlVal: Optional[float]
    upperCorpId: Optional[str]
    corpStatCdEn: str
    corpStatCdKr: str
    emplWholeVal: Optional[int]
    modifiedDate: str
    corpStockCdEn: str
    corpStockCdKr: str
    logoImageFile: Optional[str]
    finacRevenueAt: str
    niceCorpStatCd: str
    finacRevenueVal: int
    invstSumValText: str
    requestSendTypeCd: Optional[str]
    investmentDescription: str


class SeedPeople(_IgnoreExtraModel):
    id: str
    fbUrl: str
    corpId: str
    etcUrl: Optional[str]
    comment: Optional[str]
    ivstrId: Optional[str]
    useFlag: bool
    createBy: Optional[str]
    linkdUrl: str
    showFlag: bool
    pplNameEn: str
    pplNameKr: str
    pplRoleCd: str
    rocketUrl: Optional[str]
    corpNameEn: Optional[str]
    corpNameKr: Optional[str]
    createDate: Optional[str]
    crewRoleCd: Optional[str]
    hasHistory: Optional[bool]
    modifiedBy: Optional[str]
    modifiedDate: Optional[str]
    seedPeopleHistories: Optional[str]


class SeedCorpBiz(_IgnoreExtraModel):
    biz: int
    corpCnt: int
    createBy: str
    bizNameEn: str
    bizNameKr: str
    createDate: str


class SeedCorpTag(_IgnoreExtraModel):
    tag: str
    corpCnt: int
    tagNameEn: Optional[str]
    tagNameKr: str


class SeedProduct(_IgnoreExtraModel):
    id: str
    andUrl: Optional[str]
    corpId: str
    webUrl: str
    createBy: str
    isAppProd: bool
    isEtcProd: bool
    isOffProd: bool
    isWebProd: bool
    prodEndAt: Optional[str]
    createDate: str
    finishFlag: bool
    modifiedBy: Optional[str]
    prodNameEn: str
    prodNameKr: str
    prodIntroEn: str
    prodIntroKr: str
    prodLogoImg: str
    etcProdCount: Optional[int]
    modifiedDate: Optional[str]
    offProdCount: Optional[int]


class SeedBadgeItem(_IgnoreExtraModel):
    id: str
    badge: str
    endAt: str
    comment: Optional[str]
    startAt: str
    createBy: str
    showCode: str
    badgeImage: str
    bubbleText: str
    createDate: str
    modifiedBy: str
    bubbleTitle: str
    modifiedDate: str
    logoImageFile: Optional[str]
    bubbleButtonUrl: str
    bubbleButtonFlag: bool
    bubbleButtonText: str
    seedBadgeCorpCaches: Optional[dict]


class SeedAdvertisementKeyword(_IgnoreExtraModel):
    id: str
    corpCnt: int
    advertisementKeyword: str


class BaseCompanyData(_IgnoreExtraModel):
    seedCorp: SeedCorp
    seedBadge: List[SeedBadgeItem]
    seedPeople: List[SeedPeople]
    seedCorpBiz: List[SeedCorpBiz]
    seedCorpTag: List[SeedCorpTag]
    seedProduct: SeedProduct
    seedPeopleBlind: bool
    seedPeopleCount: int
    seedCorpBizBlind: bool
    seedCorpBizCount: int
    seedCorpTagBlind: bool
    seedCorpTagCount: int
    seedProductBlind: bool
    seedAdvertisementKeywords: List[SeedAdvertisementKeyword]


class OgTagContent(_IgnoreExtraModel):
    title: str
    thumbnail: str
    description: str


class BaseCompanyInfo(_IgnoreExtraModel):
    data: BaseCompanyData
    referrer: str
    userAgent: str
    ogTagContent: OgTagContent


class InvestmentData(_IgnoreExtraModel):
    data: List[dict]
    recentUpdate: str
    totalInvestmentAmount: int
    lastInvestmentLevel: str
    investmentDescription: str


class ForestOfHyuksinCompanyData(_IgnoreExtraModel):
    mau: MAUInfo
    patent: Optional[PatentInfo] = None
    finance: FinanceInfo
    products: List[Product]
    customerType: Optional[CustomerTypeInfo] = None
    organization: OrganizationInfo
    similarCorps: List[SimilarCorp]
    customerSales: Optional[CustomerSalesInfo] = None
    investment: Optional[InvestmentData] = None
    dataSufficient: bool
    base_company_info: BaseCompanyInfo
