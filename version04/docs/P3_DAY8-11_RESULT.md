# Phase 3 Day 8-11: 프론트엔드 듀얼 뷰어 + 비교 테이블 + comparison UI

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/web/static/viewer.js
   변경 유형: MODIFY
   변경 라인 수: ~55줄 추가
   의존성 변경: 없음 ($3Dmol 이미 전역)

📄 파일: src/qcviz_mcp/web/static/results.js
   변경 유형: MODIFY
   변경 라인 수: ~75줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/web/static/chat.js
   변경 유형: MODIFY
   변경 라인 수: ~80줄 추가
   의존성 변경: 없음
```

---

## Patch 1/3: viewer.js — 듀얼 3Dmol.js 뷰어

> **위치**: 파일 끝에 추가 (기존 single viewer 함수 아래)
> **이유**: comparison 모드에서 원본/변형 분자를 나란히 3D 렌더링 + 회전 동기화

```javascript
// ── Phase 3: Comparison Dual Viewer ─────────────────────────

/**
 * Initialize two side-by-side 3Dmol.js viewers for comparison mode.
 * Existing single viewer is NOT touched.
 *
 * @param {string} containerIdA - DOM id for molecule A viewer.
 * @param {string} containerIdB - DOM id for molecule B viewer.
 * @returns {{viewerA: object, viewerB: object}}
 */
function initComparisonViewers(containerIdA, containerIdB) {
    const elA = document.getElementById(containerIdA);
    const elB = document.getElementById(containerIdB);
    if (!elA || !elB) {
        console.warn('[comparison] viewer containers not found:', containerIdA, containerIdB);
        return { viewerA: null, viewerB: null };
    }
    const viewerA = $3Dmol.createViewer(elA, { backgroundColor: 'white' });
    const viewerB = $3Dmol.createViewer(elB, { backgroundColor: 'white' });
    return { viewerA, viewerB };
}

/**
 * Render molecules into the comparison viewers from result dicts.
 *
 * @param {object} viewerA - 3Dmol viewer for molecule A.
 * @param {object} viewerB - 3Dmol viewer for molecule B.
 * @param {object} resultA - Compute result dict for A (must have .xyz or .atoms).
 * @param {object} resultB - Compute result dict for B.
 */
function renderComparisonMolecules(viewerA, viewerB, resultA, resultB) {
    if (!viewerA || !viewerB) return;

    // Helper: load a result into a viewer
    function loadResult(viewer, result) {
        viewer.removeAllModels();
        if (!result) return;
        const xyz = result.xyz || result.xyz_block || '';
        if (xyz) {
            viewer.addModel(xyz, 'xyz');
        } else if (result.atoms && Array.isArray(result.atoms)) {
            // Build XYZ from atoms array
            const lines = [String(result.atoms.length), ''];
            for (const a of result.atoms) {
                lines.push(`${a.symbol || a.element || 'X'}  ${a.x} ${a.y} ${a.z}`);
            }
            viewer.addModel(lines.join('\n'), 'xyz');
        }
        viewer.setStyle({}, { stick: {}, sphere: { scale: 0.3 } });
        viewer.zoomTo();
        viewer.render();
    }

    loadResult(viewerA, resultA);
    loadResult(viewerB, resultB);
}

/**
 * Synchronize rotation/zoom between two 3Dmol viewers.
 *
 * @param {object} viewerA - Source viewer.
 * @param {object} viewerB - Target viewer (follows A's orientation).
 */
function syncViewerRotation(viewerA, viewerB) {
    if (!viewerA || !viewerB) return;
    let syncing = false;
    const syncFromA = function () {
        if (syncing) return;
        syncing = true;
        try {
            const view = viewerA.getView();
            viewerB.setView(view);
        } catch (e) { /* ignore */ }
        syncing = false;
    };
    // Use viewchanged callback if available
    if (typeof viewerA.setViewChangeCallback === 'function') {
        viewerA.setViewChangeCallback(syncFromA);
    }
}
```

---

## Patch 2/3: results.js — 비교 테이블 렌더링

> **위치**: 파일 끝에 추가
> **이유**: delta dict를 사람이 읽을 수 있는 테이블 HTML로 변환

```javascript
// ── Phase 3: Comparison Table ───────────────────────────────

/**
 * Render a property comparison table into a container element.
 *
 * @param {string} containerId - DOM id for the table container.
 * @param {object} delta - Delta dict from compute_delta().
 * @param {object} resultA - Full result dict for molecule A.
 * @param {object} resultB - Full result dict for molecule B.
 */
function renderComparisonTable(containerId, delta, resultA, resultB) {
    const container = document.getElementById(containerId);
    if (!container || !delta) return;

    const rows = [];

    // Energy
    if (delta.energy_delta_ev != null) {
        rows.push({
            property: '총 에너지 (eV)',
            valueA: delta.energy_a_ev != null ? delta.energy_a_ev.toFixed(4) : '—',
            valueB: delta.energy_b_ev != null ? delta.energy_b_ev.toFixed(4) : '—',
            delta: (delta.energy_delta_ev >= 0 ? '+' : '') + delta.energy_delta_ev.toFixed(4),
            extra: delta.energy_delta_kcal != null
                ? (delta.energy_delta_kcal >= 0 ? '+' : '') + delta.energy_delta_kcal.toFixed(2) + ' kcal/mol'
                : '',
        });
    }

    // HOMO-LUMO gap
    if (delta.gap_delta_ev != null) {
        rows.push({
            property: 'HOMO-LUMO Gap (eV)',
            valueA: delta.gap_a_ev != null ? delta.gap_a_ev.toFixed(4) : '—',
            valueB: delta.gap_b_ev != null ? delta.gap_b_ev.toFixed(4) : '—',
            delta: (delta.gap_delta_ev >= 0 ? '+' : '') + delta.gap_delta_ev.toFixed(4),
            extra: '',
        });
    }

    // HOMO energy
    if (delta.homo_energy_ev_delta != null) {
        rows.push({
            property: 'HOMO 에너지 (eV)',
            valueA: delta.homo_energy_ev_a != null ? delta.homo_energy_ev_a.toFixed(4) : '—',
            valueB: delta.homo_energy_ev_b != null ? delta.homo_energy_ev_b.toFixed(4) : '—',
            delta: (delta.homo_energy_ev_delta >= 0 ? '+' : '') + delta.homo_energy_ev_delta.toFixed(4),
            extra: '',
        });
    }

    // LUMO energy
    if (delta.lumo_energy_ev_delta != null) {
        rows.push({
            property: 'LUMO 에너지 (eV)',
            valueA: delta.lumo_energy_ev_a != null ? delta.lumo_energy_ev_a.toFixed(4) : '—',
            valueB: delta.lumo_energy_ev_b != null ? delta.lumo_energy_ev_b.toFixed(4) : '—',
            delta: (delta.lumo_energy_ev_delta >= 0 ? '+' : '') + delta.lumo_energy_ev_delta.toFixed(4),
            extra: '',
        });
    }

    // Max charge diff
    if (delta.max_charge_diff != null) {
        rows.push({
            property: '최대 전하 변화 (e)',
            valueA: '—',
            valueB: '—',
            delta: delta.max_charge_diff.toFixed(4),
            extra: delta.mean_charge_diff != null
                ? '평균: ' + delta.mean_charge_diff.toFixed(4)
                : '',
        });
    }

    // Atom count
    if (delta.atom_count_a != null && delta.atom_count_b != null) {
        rows.push({
            property: '원자 수',
            valueA: String(delta.atom_count_a),
            valueB: String(delta.atom_count_b),
            delta: String(delta.atom_count_b - delta.atom_count_a),
            extra: '',
        });
    }

    const molA = delta.molecule_a || '분자 A';
    const molB = delta.molecule_b || '분자 B';

    let html = '<table class="comparison-table">'
        + '<thead><tr>'
        + '<th>성질</th>'
        + '<th>' + molA + '</th>'
        + '<th>' + molB + '</th>'
        + '<th>Δ (차이)</th>'
        + '</tr></thead><tbody>';

    for (const row of rows) {
        const dVal = parseFloat(row.delta);
        const cls = isNaN(dVal) ? '' : (dVal > 0 ? 'delta-positive' : (dVal < 0 ? 'delta-negative' : ''));
        html += '<tr>'
            + '<td>' + row.property + '</td>'
            + '<td>' + row.valueA + '</td>'
            + '<td>' + row.valueB + '</td>'
            + '<td class="' + cls + '">' + row.delta
            + (row.extra ? '<br><small>' + row.extra + '</small>' : '')
            + '</td></tr>';
    }
    html += '</tbody></table>';

    // Convergence warning
    if (delta.both_converged === false) {
        html += '<div class="comparison-warning">'
            + '⚠️ 하나 이상의 계산이 완전히 수렴하지 않았을 수 있습니다.'
            + '</div>';
    }

    container.innerHTML = html;
}

/**
 * Render a natural-language explanation card.
 *
 * @param {string} containerId - DOM id for the explanation container.
 * @param {object} explanation - Explanation dict from explain_comparison().
 */
function renderExplanationCard(containerId, explanation) {
    const el = document.getElementById(containerId);
    if (!el || !explanation) return;

    let html = '<div class="comparison-explanation-card">';
    if (explanation.summary) {
        html += '<p class="explanation-summary">' + explanation.summary + '</p>';
    }
    if (explanation.key_findings && explanation.key_findings.length) {
        html += '<ul class="explanation-findings">';
        for (const f of explanation.key_findings) {
            html += '<li>' + f + '</li>';
        }
        html += '</ul>';
    }
    if (explanation.interpretation && explanation.interpretation.length) {
        html += '<div class="explanation-interpretation"><strong>해석:</strong><ul>';
        for (const i of explanation.interpretation) {
            html += '<li>' + i + '</li>';
        }
        html += '</ul></div>';
    }
    if (explanation.cautions && explanation.cautions.length) {
        html += '<div class="explanation-cautions"><strong>주의:</strong><ul>';
        for (const c of explanation.cautions) {
            html += '<li>' + c + '</li>';
        }
        html += '</ul></div>';
    }
    html += '</div>';
    el.innerHTML = html;
}
```

---

## Patch 3/3: chat.js — comparison WebSocket 메시지 핸들링

### 변경 A: 기존 `onmessage` handler의 `switch(data.type)` 내부에 case 추가

> **위치 찾기**:
> ```bash
> grep -n "case.*type\|switch.*data\.type\|msg_type\|data.type" \
>   src/qcviz_mcp/web/static/chat.js | head -20
> ```
>
> **삽입 지점**: 기존 case 블록 영역 (예: `case 'result':` 근처)

```javascript
        // ── Phase 3: Comparison messages ────────────────────
        case 'comparison_started':
            appendChatMessage('system',
                data.message || '비교 계산을 시작합니다...');
            showComparisonLoader(data.targets || []);
            break;

        case 'comparison_result':
            hideComparisonLoader();
            if (data.result) {
                renderComparisonView(data.result);
                if (data.message) {
                    appendChatMessage('assistant', data.message);
                }
            }
            break;

        case 'comparison_error':
            hideComparisonLoader();
            appendChatMessage('error',
                data.message || '비교 계산 중 오류가 발생했습니다.');
            break;
```

### 변경 B: 헬퍼 함수들 (chat.js 끝에 추가)

```javascript
// ── Phase 3: Comparison UI helpers ──────────────────────────

/**
 * Show a loading indicator for comparison mode.
 * @param {string[]} targets - Names of the two molecules being compared.
 */
function showComparisonLoader(targets) {
    const loader = document.getElementById('comparison-loader');
    if (loader) {
        const names = targets.length >= 2
            ? targets[0] + ' vs ' + targets[1]
            : '비교 계산';
        loader.innerHTML = '<div class="comparison-loading">'
            + '<div class="spinner"></div>'
            + '<span>' + names + ' 계산 중...</span>'
            + '</div>';
        loader.style.display = 'block';
    }
}

/**
 * Hide the comparison loading indicator.
 */
function hideComparisonLoader() {
    const loader = document.getElementById('comparison-loader');
    if (loader) {
        loader.style.display = 'none';
        loader.innerHTML = '';
    }
}

/**
 * Main entry point: render a complete comparison view from a
 * comparison_result WebSocket message payload.
 *
 * @param {object} result - The comparison result object containing
 *   result_a, result_b, delta, explanation, method, basis.
 */
function renderComparisonView(result) {
    if (!result) return;

    // 1. Show the comparison container
    const container = document.getElementById('comparison-container');
    if (!container) {
        console.warn('[comparison] #comparison-container not found');
        return;
    }
    container.style.display = 'block';

    const molA = (result.delta && result.delta.molecule_a) || '분자 A';
    const molB = (result.delta && result.delta.molecule_b) || '분자 B';
    const methodStr = (result.method || '') + (result.basis ? ' / ' + result.basis : '');

    container.innerHTML = ''
        + '<div class="comparison-header">'
        +   '<h3>비교 결과: ' + molA + ' vs ' + molB + '</h3>'
        +   (methodStr ? '<span class="comparison-method">' + methodStr + '</span>' : '')
        +   '<button class="comparison-close" onclick="closeComparisonView()" '
        +     'title="닫기">&times;</button>'
        + '</div>'
        + '<div class="comparison-viewers">'
        +   '<div class="comparison-viewer-wrap">'
        +     '<div class="comparison-viewer-label">' + molA + '</div>'
        +     '<div id="comparison-viewer-a" class="comparison-viewer"></div>'
        +   '</div>'
        +   '<div class="comparison-viewer-wrap">'
        +     '<div class="comparison-viewer-label">' + molB + '</div>'
        +     '<div id="comparison-viewer-b" class="comparison-viewer"></div>'
        +   '</div>'
        + '</div>'
        + '<div id="comparison-table-container"></div>'
        + '<div id="comparison-explanation"></div>';

    // 2. Dual 3Dmol viewers
    const { viewerA, viewerB } = initComparisonViewers(
        'comparison-viewer-a', 'comparison-viewer-b'
    );
    renderComparisonMolecules(
        viewerA, viewerB,
        result.result_a || {}, result.result_b || {}
    );
    syncViewerRotation(viewerA, viewerB);

    // 3. Comparison table
    if (result.delta) {
        renderComparisonTable(
            'comparison-table-container',
            result.delta,
            result.result_a || {},
            result.result_b || {}
        );
    }

    // 4. Explanation card
    if (result.explanation) {
        renderExplanationCard('comparison-explanation', result.explanation);
    }

    // 5. Handle partial failure
    if (result.error_a) {
        appendChatMessage('warning',
            '분자 A 계산 실패: ' + result.error_a);
    }
    if (result.error_b) {
        appendChatMessage('warning',
            '분자 B 계산 실패: ' + result.error_b);
    }
}

/**
 * Close the comparison view and reset the container.
 */
function closeComparisonView() {
    const container = document.getElementById('comparison-container');
    if (container) {
        container.style.display = 'none';
        container.innerHTML = '';
    }
}
```

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

# 1. viewer.js 듀얼 뷰어 함수
grep -n "initComparisonViewers\|renderComparisonMolecules\|syncViewerRotation" \
  src/qcviz_mcp/web/static/viewer.js
# 기대: 3줄 (함수 정의)

# 2. results.js 비교 테이블
grep -n "renderComparisonTable\|renderExplanationCard" \
  src/qcviz_mcp/web/static/results.js
# 기대: 2줄

# 3. chat.js comparison 메시지 핸들러
grep -n "comparison_started\|comparison_result\|renderComparisonView\|closeComparisonView" \
  src/qcviz_mcp/web/static/chat.js
# 기대: 5줄 이상

# 4. 서버 기동 후 브라우저에서 확인
# → "벤젠과 톨루엔 비교해줘" 입력
# → comparison_started → loading → comparison_result → 듀얼 뷰어 + 테이블
```

---

## 다음 Day 연결점

- **Day 12-14**: `style.css`에 comparison 레이아웃 CSS 추가
  (`.comparison-container`, `.comparison-viewers` grid, `.comparison-table`,
  `.delta-positive`/`.delta-negative` 색상, 반응형).
  `index.html`에 `#comparison-container`, `#comparison-loader` DOM 요소 추가.
  Edge case 처리 (한쪽 실패, 동일 구조 비교, 빈 delta) + 통합 테스트.
