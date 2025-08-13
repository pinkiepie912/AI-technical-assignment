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
            주어진 정보를 바탕으로 이 인재가 보유한 경험과 역량을 정확하게 분석하고, 
            객관적 근거와 함께 한국어 태그로 추론해주세요.
            경력 사항에 작성된 직책명, 업무 내용, 회사 성장 지표 등을 종합적으로 고려하여
            경험 태그를 도출해야 합니다.

            ## 📋 인재 기본 정보
            **업계**: {{ talent_profile.industryName }}

            **보유 스킬**: 
            {% if talent_profile.skills %}
            {% for skill in talent_profile.skills %}
            - {{ skill }}
            {% endfor %}
            {% else %}
            정보 없음
            {% endif %}

            ## 🎓 교육 배경
            {% if talent_profile.educations %}
            {% for education in talent_profile.educations %}
            **{{ education.schoolName }}**
            - 학위: {{ education.degreeName }}
            - 전공: {{ education.fieldOfStudy }}
            - 기간: {{ education.startEndDate }}
            - 성적: {{ education.grade }}
            {% endfor %}
            {% else %}
            교육 정보 없음
            {% endif %}

            ## 💼 경력 사항
            {% if talent_profile.positions %}
            {% for position in talent_profile.positions %}
            **{{ position.companyName }}** - {{ position.title }}
            - 위치: {{ position.companyLocation }}
            - 재직기간: {{ position.startEndDate.start.year }}년 
            {{ position.startEndDate.start.month or 1 }}월 ~
            {% if position.startEndDate.end %} 
            {{ position.startEndDate.end.year }}년 {{ position.startEndDate.end.month or 12 }}월
            {% else %}현재{% endif %}
            - 업무설명: {{ position.description }}
            {% endfor %}
            {% else %}
            경력 정보 없음
            {% endif %}

            ## 🏢 회사 상세 정보 및 재직 기간 분석
            {% if company_summaries %}
            {% for company in company_summaries %}
            ### {{ company.name }}{% if company.name_en %} ({{ company.name_en }}){% endif %}

            **기업 개요**:
            - 사업분야: {{ company.industry | join(', ') }}
            - 비즈니스 태그: {{ company.tags | join(', ') }}
            - 투자단계: {{ company.stage or '정보 없음' }}
            - 설립일: {{ company.founded_date or '정보 없음' }}
            - 기업연령: {{ company.company_age_years or '정보 없음' }}년
            - 스타트업 여부: {{ '예' if company.is_startup else '아니오' }}
            - IPO 날짜: {{ company.ipo_date or '정보 없음' }}
            {% if company.business_description %}
            - 사업 설명: {{ company.business_description }}
            {% endif %}

            **재직 기간 중 회사 성장 지표**:
            - 직원 수: {{ company.metrics.people_count }}명 
            (성장률: {{ "%.1f" | format(company.metrics.people_growth_rate) }}%)
            - 매출: {{ "{:,}".format(company.metrics.profit) }}원 
            (성장률: {{ "%.1f" | format(company.metrics.profit_growth_rate) }}%)
            - 순이익: {{ "{:,}".format(company.metrics.net_profit) }}원 
            (성장률: {{ "%.1f" | format(company.metrics.net_profit_growth_rate) }}%)
            - 투자 유치액: {{ "{:,}".format(company.metrics.investment_amount) }}원
            - 주요 투자자: {{ company.metrics.investors | join(', ') }}

            {% if company.metrics.patents %}
            **보유 특허**:
            {% for patent in company.metrics.patents %}
            - {{ patent.level }}: {{ patent.title }}
            {% endfor %}
            {% endif %}

            {% if company.metrics.maus %}
            **MAU 정보**:
            {% for mau in company.metrics.maus %}
            - {{ mau.product_name }}: {{ "{:,}".format(mau.value) }}명 
            (성장률: {{ "%.1f" | format(mau.growth_rate) }}%)
            {% endfor %}
            {% endif %}

            **회사 별칭/식별명**: {{ company.aliases | join(', ') }}

            ---
            {% endfor %}
            {% else %}
            회사 정보 없음
            {% endif %}

            ## 🎯 경험 태그 추론 가이드라인

            다음 기준에 따라 객관적 근거와 함께 경험 태그를 추론해주세요:

            ### 1. 교육 배경 관련
            - **상위권대학교**: 서울대학교, 연세대학교, 고려대학교, KAIST, POSTECH, 서강대학교, 
            성균관대학교, 한양대학교 등 국내 상위권 대학 졸업

            ### 2. 기업 규모 및 특성 관련
            - 대규모회사경험: 대기업(삼성, LG, KT, SK, 네이버, 카카오 등), 글로벌 기업에서의 근무 경험
            - 성장기스타트업경험: 스타트업에서 재직 중 조직 인원 규모나 투자 규모가 2배 이상 성장한 경험
            - 성장기스타트업 경험: [기업]에서 재직 중 [투자, 조직, 매출] 규모 N배 이상 성장

            ### 3. 리더십 및 관리 관련
            - **리더십경험**: CTO, CFO, CPO, Director, 팀장, 챕터리드, 테크리드 등 리더십 포지션 경험

            ### 4. 기술 및 도메인 관련
            - **대용량데이터처리경험**: 빅데이터, AI/ML, 검색엔진, 추천시스템, NLP, 하이퍼클로바 등 
            대규모 데이터 처리 기술 경험

            ### 5. 비즈니스 경험 관련
            - **M&A경험**: 인수합병, 사모펀드 매각, 기업 인수 관련 업무 경험
            - **IPO경험**: 기업공개, 상장 관련 업무 경험 (재직 중 회사 IPO 포함)
            - **신규투자유치경험**: 시리즈 A/B/C/D/E/F 등 투자 유치 업무 참여 경험

            ### 6. 추가 도메인 경험
            - **글로벌사업경험**: 해외 진출, 글로벌 서비스 런칭 경험
            - **B2C/B2B도메인경험**: 해당 비즈니스 모델에서의 실무 경험
            - **물류/커머스/핀테크/게임/미디어도메인경험**: 특정 산업 도메인 전문성

            ## 📝 응답 형식 및 요구사항

            **중요**: 반드시 아래 형식으로만 응답하세요.

            ```json
            {
              "experience_tags": ["태그1", "태그2", "태그3"],
              "reasoning": {
                "태그1": "추론 근거와 객관적 사실",
                "태그2": "추론 근거와 객관적 사실", 
                "태그3": "추론 근거와 객관적 사실"
              }
            }
            ```

            **추론 시 고려사항**:
            1. 객관적 사실과 데이터에 기반한 추론
            2. 재직 기간과 회사의 성장 지표 연관성 분석
            3. 직책명과 업무 내용의 구체적 분석
            4. 회사의 사업 특성과 개인 역할의 연관성
            5. 시간순 경력 발전 패턴 분석

            """

        return RichPromptTemplate(template_str=template_str)
