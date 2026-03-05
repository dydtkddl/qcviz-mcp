# QCViz-MCP 기여 가이드 (Contributing Guide)

프로젝트에 관심을 가져주셔서 감사합니다! QCViz-MCP는 누구나 참여할 수 있는 오픈소스 프로젝트입니다.

## 개발 환경 설정

1. 저장소를 클론합니다.

   ```bash
   git clone https://github.com/user/qcviz-mcp.git
   cd qcviz-mcp
   ```

2. 변경 사항을 테스트하기 위해 `dev` 옵션을 포함하여 설치합니다.
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

## 코드 스타일 강제 (Code Style)

저희는 향상된 속도와 일관된 포매팅을 위해 **ruff**를 사용합니다. 커밋하기 전에 린터와 포매터를 통과해야 합니다.

```bash
ruff check src tests
```

## 테스트 (Testing)

새로운 백엔드나 도구를 추가할 때는 반드시 짝이 맞는 테스트 파일(`tests/test_*.py`)을 함께 작성해 주시기 바랍니다. 의존성이 없는 환경에서도 스킵 처리되도록 `pytest.importorskip` 구문을 활용하세요.

```bash
pytest --cov=src/qcviz_mcp tests/
```

## 새 백엔드 추가하기

이 프로젝트는 유연한 `BackendRegistry` 아키텍처를 채택하고 있습니다. 새로운 양자화학 프로그램 지원이나 시각화 도구를 추가하려면:

1. `src/qcviz_mcp/backends/` 에 새 모듈을 생성하고 (예: `new_backend.py`) 지정된 Base 클래스를 상속받아 구현하세요.
2. 미설정 시의 에러 처리를 위해 `try/except ImportError` 블록을 활용하여 부드러운 하위 호환성을(graceful degradation) 유지해 주세요.
3. PR(Pull Request) 생성 전 충분한 단위 테스트를 완료해 주십시오.

## Pull Request 안내

- PR 제목은 Conventional Commits 형식(`feat(backend): add xyz`)을 따라 주세요.
- 문제 설명, 변경된 테스트 내역을 기재해 주시기 바랍니다.
