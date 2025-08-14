from llama_index.core.prompts import RichPromptTemplate


class TalentInferencePromptTemplates:
    """
    인재 추론을 위한 프롬프트 템플릿 관리 객체
    """

    @staticmethod
    def get_talent_experience_inference_template() -> RichPromptTemplate:
        """
        인재의 경험과 역량을 추론하기 위한 프롬프트 템플릿을 반환합니다.

        Returns:
            RichPromptTemplate: TalentProfile과 CompanySummary를 파라미터로 받는 템플릿
        """
        template_str = """
            주어진 정보(재직기간내 회사의 투자/매출/MAU/조직규모/뉴스 등)를 바탕으로 이 인재가 보유한 경험을 정확하게 분석하고, 객관적 근거와 함께 경험과 역량을 한국어 태그로 추론해주세요.

            ## 교육 배경
            {% if talent_profile.educations %}
            {% for education in talent_profile.educations %}
            {{ education.schoolName }}
            - 학위: {{ education.degreeName }}
            - 전공: {{ education.fieldOfStudy }}
            {% endfor %}
            {% else %}
            교육 정보 없음
            {% endif %}

            ## 경력 및 관련 컨텍스트
            {% if chronological_contexts %}
            {% for context in chronological_contexts %}
            {% set position = context.position %}
            {% set company_context = context.company_context %}
            {% set related_news = context.related_news %}

            ### {{ position.companyName }} - {{ position.title }}
            재직기간: {{ position.startEndDate.start.year }}년 {{ position.startEndDate.start.month or 1 }}월 ~ {% if position.startEndDate.end %}{{ position.startEndDate.end.year }}년 {{ position.startEndDate.end.month or 12 }}월{% else %}현재{% endif %}  
            업무설명: {{ position.description }}

            {% if company_context %}
            {% set company = company_context.company %}
            {% set metrics = company_context.metrics %}

            회사 상세 정보:
            - 사업분야: {{ company.industry | join(', ') }}
            - 비즈니스 태그: {{ company.tags | join(', ') }}
            - IPO 날짜: {{ company.ipo_date or '정보 없음' }}
            {% if company.business_description %}
            - 설립 날짜: {{ company.founded_date or '정보 없음' }}
            - 사업 설명: {{ company.business_description }}
            {% endif %}

            재직 기간 중 회사 성장 지표:
            - 직원 수: {{ metrics.people_count }}명 (성장률: {{ "%.1f" | format(metrics.people_growth_rate) }}%)
            - 매출: {{ "{:,}".format(metrics.profit) }}원 (성장률: {{ "%.1f" | format(metrics.profit_growth_rate) }}%)
            - 순이익: {{ "{:,}".format(metrics.net_profit) }}원 (성장률: {{ "%.1f" | format(metrics.net_profit_growth_rate) }}%)
            - 투자 시리즈: {{ metrics.levels | join(', ') or '정보 없음' }}
            - 투자 유치액: {{ "{:,}".format(metrics.investment_amount) }}원
            - 주요 투자자: {{ metrics.investors | join(', ') }}

            {% if metrics.maus %}
            MAU 정보:
            {% for mau in metrics.maus %}
            - {{ mau.product_name }}: {{ "{:,}".format(mau.value) }}명 (성장률: {{ "%.1f" | format(mau.growth_rate) }}%)
            {% endfor %}
            {% endif %}
            {% else %}
            회사 정보: 상세 정보 없음
            {% endif %}

            {% if related_news %}
            재직기간 관련 뉴스:
            {% for news in related_news %}
            - {{ news.title }} — {{ news.contents }}
            {% endfor %}
            {% else %}
            관련 뉴스: 없음
            {% endif %}

            ---

            {% endfor %}
            {% else %}
            경력 정보 없음
            {% endif %}

            ## 경험 태그 추론 가이드라인
            ### 1. 교육 배경 관련
            - 상위권대학교: 서울대학교, 연세대학교, 고려대학교, KAIST, POSTECH 등 국내 기준 상위권 대학 졸업

            ### 2. 기업 규모 및 특성 관련
            - 대규모회사경험: 대기업(삼성, LG, KT, SK 등), 글로벌 기업에서의 근무 경험
            - 성장기스타트업경험: 스타트업 재직 중 조직이나 투자 규모가 성장한 경험

            ### 3. 리더십 및 관리 관련
            - 리더십경험: CTO, CFO, CPO, Director, 팀장, 챕터리드, 테크리드 등 리더십 포지션 경험

            ### 4. 기술 및 도메인 관련
            - 대용량데이터처리경험: 빅데이터, AI/ML, 검색엔진, 추천시스템, NLP 등 대규모 데이터 처리 기술 경험

            ### 5. 비즈니스 경험 관련
            - M&A경험: 인수합병, 사모펀드 매각, 기업 인수 관련 업무 경험이나 재직중 M&A 경험
            - IPO경험: 기업공개, 상장 관련 업무 경험 (재직 중 회사 IPO 포함)
            - 신규투자유치경험: 시리즈 A/B/C/D/E/F 등 투자사로부터 투자 유치 업무 참여 경험.

            ### 6. 추가 도메인 경험
            - 글로벌사업경험: 해외 진출, 글로벌 서비스 런칭 경험
            - B2C 도메인 경험
            - B2B도메인경험
            - 특정 산업 도메인 전문성: 물류/커머스/핀테크/게임/미디어

            ## 역량 태그 추론 가이드라인
            ### 1. 리더십 역량
            ### 2. 데이터엔지니어링 역량
            ### 3. 커뮤니케이션 역량
            ### 4. 기타 역량

            ## 응답 형식
            ```json
            {
              "experience_tags": ["경험 태그", "태그2", "태그3"],
              "competency_tags": ["역량 태그", "태그2", "태그3"],
              "inferences": [
                {tag: "태그1", inference: "직책명·업무·성장지표·사업특성·뉴스를 포함한 경험/역량 추론"},
                {tag: "태그2", inference: "추론 근거"},
                {tag: "태그3", inference: "추론 근거"}
              ]
            }

            ## **필수 조건**
            1. 객관적 데이터, 뉴스 기반 추론 (성장 지표·직책명·업무·뉴스 포함)
            2. 회사 사업 특성과 개인 역할 연관성 분석
            3. 모든 경력을 시간순 분석
            4. 반드시 JSON만 출력, 다른 설명 금지
            5. 각 추론은 반드시 3문장 이상 작성
            6. 제약 위반 시 스스로 수정 후 출력
            
            ## 예시 출력(Few-shot) 
            ### 기대 출력
            ```json
            {
              "experience_tags": ["상위권대학교", "대규모회사경험", "대용량데이터처리경험", "리더십경험", "성장기스타트업경험", "글로벌사업경험", "신규투자유치경험"],
              "competency_tags": ["리더십", "데이터엔지니어링", "커뮤니케이션"],
              "inferences": [
                { "tag": "상위권대학교", "inference": "서울대학교 컴퓨터공학과 졸업" },
                { "tag": "대규모회사경험", "inference": "네이버와 삼성전자 같은 국내 최고 IT 기업에서 Tech Lead와 백엔드 엔지니어로 근무하며, 수천 명 규모의 조직에서 대규모 검색 서비스를 성공적으로 설계하고 운영했습니다. 이는 복잡한 시스템 아키텍처 설계 능력과 유기적인 협업 역량을 증명하는 대규모 회사 경험의 핵심 지표입니다." },
                { "tag": "대용량데이터처리경험", "inference": "네이버에서 대규모 한국어 LLM(거대 언어 모델) 개발 프로젝트를 리드하며, 수십 테라바이트(TB)에 달하는 데이터 처리 파이프라인을 직접 설계하고 구축한 경험이 있습니다. 이는 최신 AI 기술 트렌드에 대한 이해와 실제 서비스에 적용 가능한 대용량 데이터 처리 경험을 보유했음을 보여줍니다." },
                { "tag": "리더십", "inference": "AB에서 15명 규모의 백엔드 개발팀을 이끌고 '클로바X'의 개발을 총괄하며 팀의 목표 달성을 성공적으로 주도했습니다. 이는 단순한 기술 역량을 넘어, 팀원의 성장을 이끌고 비즈니스 목표를 완수하는 검증된 리더십을 갖추었음을 의미합니다." },
                { "tag": "성장기스타트업경험", "inference": "초기 멤버로 합류한 스타트업이 직원 수 10명에서 50명으로 빠르게 성장하는 과정을 주도적으로 경험했습니다. 이는 불확실한 환경 속에서 빠른 실행력으로 비즈니스 성장에 직접 기여하는 성장기 스타트업 경험을 보유했다는 강력한 증거입니다." },
                { "tag": "신규투자유치경험", "inference": "핵심 기술과 성장 로드맵을 바탕으로 유수 투자사로부터 시리즈 B, C, D 단계의 투자를 성공적으로 유치하는 데 핵심적인 역할을 수행했습니다. 이는 기술 전문성을 넘어 사업의 가치를 투자자에게 증명해내는 귀중한 신규 투자 유치 경험을 갖추었다는 것을 보여줍니다." }
              ]
            }

            """

        return RichPromptTemplate(template_str=template_str)
