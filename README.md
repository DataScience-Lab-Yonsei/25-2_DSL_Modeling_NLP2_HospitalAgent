# 25-2_DSL_Modeling_NLP2_HospitalAgent

# Hospital Reservation System with Multi-Agent Orchestration

> This project was conducted by the **Natural Language Processing Team 2** as part of the 2025 Fall modeling project at [**Data Science Lab, Yonsei University**](https://github.com/DataScience-Lab-Yonsei).

병원 예약 시스템을 위한 LangGraph 기반 Multi-Agent Chat System입니다.

---

## 👥 Team

| Cohort | Members                            |
|--------|------------------------------------|
| 12th   | Eunhee Kim, Kunwoo Kim |
| 13th   | Sehyun Park (Leader)        |
| 14th   | Dongjun Shin, Junho Yeo        |

---

## 📊 Coverpage

![Cover Image](./fig/cover.png)

For more detailed explanations, methodology, and analysis, please refer to the [project report](https://docs.google.com/viewer?url=https://raw.githubusercontent.com/jwlee9941/SCOPE/main/report/report.pdf)

---

## 🚀 Quick Start

### How to Run Code

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install langgraph-cli

# 2. Set up environment variables
cp env_example.txt .env
# Edit .env file with your API keys (OPENAI_API_KEY, TAVILY_API_KEY, etc.)

# 3. Start the RAG server (in first terminal)
cd rag_doctor_agent && python a2a_wrapper.py

# 4. Run LangGraph (in second terminal)
cd ../ && langgraph dev

# 5. (Optional) Use custom chat interface (in third terminal)
# LangGraph Studio UI automatically launches in the browser when you run `langgraph dev`
# But you can also use the custom terminal interface:
python chat_interface.py
```

**접속 정보:**
- **LangGraph Studio UI**: `http://localhost:8123` (자동으로 브라우저에서 열림)
- **Chat Interface**: 터미널에서 `python chat_interface.py` 실행

---

## 🏗️ 아키텍처

### 새로운 3-Agent 시스템
```
사용자 입력
    ↓
에이전트1(관리자) 🎯
    ├─ 예약 관련 → 에이전트2(예약) 📅
    ├─ 증상-의료진 매핑 → 에이전트3(RAG) 🧠  
    └─ 병원 정보 → Tavily 검색 툴 🔍

에이전트2(예약) 📅
    ├─ 사용자 정보 수집 (LLM 기반)
    ├─ 증상 수집 → 에이전트3 호출
    └─ Supabase 툴들 (조회/생성/변경)

에이전트3(RAG) 🧠
    └─ 기존 rag_doctor_agent 활용
```

### 폴더 구조
```
medical_reservation_agent/
├── chat_interface.py        # 💬 터미널 채팅 인터페이스
├── graph.py                 # 📊 LangGraph 진입점
├── langgraph.json           # LangGraph Studio 설정 파일
├── main/
│   ├── agents/              # 🤖 에이전트들
│   │   ├── agent1_manager.py      # 관리자 에이전트
│   │   ├── agent2_reservation.py  # 예약 에이전트
│   │   └── agent3_rag.py          # RAG 에이전트
│   ├── tools/               # 🔧 툴들
│   │   ├── tavily_search.py       # Tavily 웹검색 툴
│   │   └── supabase_mcp_tool.py   # Supabase MCP 툴
│   ├── langgraph_workflow.py      # LangGraph 워크플로우 정의
│   └── langgraph_state.py         # 상태 모델 정의
├── rag_doctor_agent/        # 🧠 RAG 서버
│   ├── a2a_wrapper.py             # Agent-to-Agent 래퍼
│   └── main/                      # RAG 파이프라인
└── test/                    # 🧪 테스트 파일들
```

---

## 📋 환경 변수 설정

`.env` 파일 생성 후 다음 API 키들을 설정하세요:

**필수:**
- `OPENAI_API_KEY`: OpenAI API 키 (LLM 사용)
- `TAVILY_API_KEY`: Tavily 검색 API 키 (병원 정보 검색)

**선택사항:**
- `LANGSMITH_*`: LangSmith 추적 (워크플로우 디버깅)
  - LangSmith 계정: https://smith.langchain.com/
- `SUPABASE_*`: Supabase 데이터베이스 (예약 관리)
  - Supabase 프로젝트에서 URL과 키 발급

---

## 💬 사용 방법

### 1. LangGraph Studio UI (추천)
```bash
langgraph dev
```
- 브라우저에서 자동으로 `http://localhost:8123` 열림
- 그래픽 인터페이스로 워크플로우 시각화
- 실시간 디버깅 및 추적 가능

### 2. 터미널 채팅 인터페이스
```bash
python chat_interface.py
```

**주요 기능:**
- 💬 실시간 대화 인터페이스
- 📝 세션 관리 및 컨텍스트 유지
- 🔧 시스템 명령어 (`/help`, `/status`, `/history`, `/save` 등)
- 🎯 다중 턴 예약 플로우
- 💾 대화 저장/불러오기

**사용 예시:**
```
👤 사용자: 예약하고 싶어요
🤖 어시스턴트: 📋 **예약 정보 수집 중**
누락된 정보: 환자명, 전화번호

👤 사용자: 홍길동입니다. 010-1234-5678이에요
🤖 어시스턴트: ✅ **예약 정보 수집 완료**
어떤 증상으로 예약하시나요?
```

**자세한 사용법:** `CHAT_GUIDE.md` 참고

---

## 🧪 테스트

### 테스트 파일 실행
```bash
# 각 에이전트 개별 테스트
python test/test_agent1_routing.py      # Agent1 라우팅 테스트
python test/test_rag_agent.py          # RAG Agent 테스트

# 통합 테스트
python test/test_full_system.py        # 전체 시스템 통합 테스트
python test/test_multi_turn_conversation.py  # 다중 턴 대화 테스트
python test/test_schedule_booking.py    # 예약 플로우 테스트

# 툴 테스트
python test/test_tool_calling.py       # Supabase MCP 툴 테스트
```

### LangGraph Studio에서 테스트
`langgraph dev` 실행 후 브라우저에서:
- `medical_reservation` 그래프 선택
- 워크플로우 시각화 확인
- 각 노드별 실행 상태 모니터링
- 실시간 디버깅

## 🤖 에이전트 시스템 설명

### 에이전트1 (관리자) 🎯
- **역할**: LLM 기반 사용자 입력 분석 및 지능형 라우팅
- **분기 로직**:
  - 예약 관련 요청 → 에이전트2(예약)
  - 증상-의료진 매핑 요청 → 에이전트3(RAG)
  - 병원 정보 요청 → Tavily 검색 툴
- **특징**: 프롬프트 기반 의도 분류, LLM을 활용한 지능형 판단

### 에이전트2 (예약) 📅
- **역할**: LLM 기반 예약 관련 모든 처리 (생성, 확인, 취소)
- **기능**:
  - 프롬프트 기반 사용자 정보 수집 (이름, 성별, 연락처)
  - 누락된 정보에 대한 친절한 재요청
  - 증상 수집 후 에이전트3 호출
  - Supabase 툴을 사용한 예약 관리
- **특징**: LLM이 사용자 입력을 이해하고 적절히 응답

### 에이전트3 (RAG) 🧠
- **역할**: 증상을 기반으로 적절한 의료진 추천
- **기능**:
  - 기존 `rag_doctor_agent` 활용
  - 증상 분석 및 진료과 매핑
  - 의료진 추천 및 신뢰도 제공
- **특징**: 기존 RAG 파이프라인 재사용

### 툴들 🔧

#### Tavily 검색 툴
- **용도**: 바른마디병원 웹사이트(https://barunjoint.kr/) 전용 검색
- **제한사항**: 반드시 해당 도메인에서만 검색
- **검색 유형**: 휴무일, 운영시간, 연락처, 위치 등

#### Supabase 툴들 (4개 전문화)
- **supabase_read_tool**: 예약 데이터 조회 (슬롯 조회, 환자 예약 목록)
- **supabase_create_tool**: 새 예약 생성
- **supabase_update_tool**: 예약 정보 수정
- **supabase_delete_tool**: 예약 취소
- **특징**: 각 작업별로 전문화된 별도 툴, 프롬프트 기반 자동 선택

## 🔄 워크플로우 흐름

1. **사용자 입력** → 에이전트1(관리자)
2. **의도 분석** → 적절한 에이전트/툴 선택
3. **라우팅**:
   - 예약 → 에이전트2 → 필요시 에이전트3 호출 → Supabase MCP 툴
   - 의료진 추천 → 에이전트3 → RAG 파이프라인
   - 병원 정보 → Tavily 검색 툴
4. **응답 생성** → 사용자에게 결과 전달

---

## 📝 주요 기능

- ✅ **Multi-Agent Orchestration** - 3개 에이전트의 협업 시스템
- ✅ **LangGraph 워크플로우** - 상태 기반 워크플로우 관리
- ✅ **RAG 기반 의료진 추천** - 증상 분석 및 적절한 의료진 매핑
- ✅ **실시간 채팅 인터페이스** - 터미널 및 LangGraph Studio UI
- ✅ **세션 관리** - 사용자별 대화 컨텍스트 유지
- ✅ **Supabase MCP 통합** - 예약 데이터 관리
- ✅ **Tavily 웹 검색** - 병원 정보 실시간 검색
- ✅ **LangSmith 추적** - 워크플로우 디버깅 및 성능 분석

---

## 🛠️ 개발 및 디버깅

### LangSmith 연동
LangGraph Studio에서 워크플로우 실행을 추적하고 디버깅할 수 있습니다:
- **LangSmith 대시보드**: https://smith.langchain.com
- 모든 LLM 호출, 에이전트 실행, 도구 사용 추적
- 성능 분석 및 최적화

### 로그 확인
각 에이전트 실행 시 상세한 로그가 콘솔에 출력됩니다:
```
🎯 Agent1: 사용자 의도 분석 중...
📅 Agent2: 예약 정보 수집 중...
🧠 Agent3: RAG 기반 의료진 추천...
✅ 워크플로우 완료
```

---

## 📚 추가 문서

- **CHAT_GUIDE.md**: 채팅 인터페이스 상세 사용법
- **LANGGRAPH_STUDIO_SETUP.md**: LangGraph Studio 설정 가이드
- **MCP_SERVER_SETUP.md**: MCP 서버 설정 방법
- **test/TEST_GUIDE.md**: 테스트 실행 가이드

---

## 📞 문제 해결

문제가 발생하면 다음을 확인해주세요:
1. 모든 의존성이 설치되었는지 확인 (`pip install -r requirements.txt`)
2. RAG 서버가 실행 중인지 확인 (`python rag_doctor_agent/a2a_wrapper.py`)
3. 환경 변수가 올바르게 설정되었는지 확인 (`.env` 파일)
4. LangGraph Studio에서 워크플로우 상태 확인
5. LangSmith에서 에러 로그 확인

---

## 📄 License

This project is part of the Data Science Lab, Yonsei University modeling project.
