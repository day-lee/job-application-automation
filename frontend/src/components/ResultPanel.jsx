import React from 'react'

/**
 * ResultPanel 컴포넌트
 * 필터링 결과, 통계, 에러 메시지 표시
 */
function ResultPanel({ result, error, isLoading }) {
  if (isLoading) {
    return null
  }

  if (error) {
    return (
      <div className="result-section error-result">
        <h2>⚠️ 오류 발생</h2>
        <p className="error-message">{error}</p>
      </div>
    )
  }

  if (!result) {
    return null
  }

  const { 
    total, 
    duplicatesRemoved, 
    passed, 
    filtered, 
    savedToSheet, 
    rejected, 
    sheetUrl, 
    message 
  } = result

  return (
    <div className="result-section success-result">
      <h2>✅ 필터링 완료</h2>

      {/* 메인 메시지 */}
      <div className="result-summary">
        <p className="main-message">
          전체 <strong>{total}</strong>개 중 <strong>{passed}</strong>개 통과,
          구글 시트에 <strong>{savedToSheet}</strong>개 저장됨
        </p>
      </div>

      {/* 통계 요약 */}
      <div className="stats-grid">
        <div className="stat-card total">
          <div className="stat-label">전체</div>
          <div className="stat-value">{total}</div>
        </div>
        
        <div className="stat-card passed">
          <div className="stat-label">통과</div>
          <div className="stat-value">{passed}</div>
        </div>

        <div className="stat-card filtered">
          <div className="stat-label">탈락</div>
          <div className="stat-value">{filtered}</div>
        </div>

        {duplicatesRemoved > 0 && (
          <div className="stat-card duplicates">
            <div className="stat-label">중복 제거</div>
            <div className="stat-value">{duplicatesRemoved}</div>
          </div>
        )}
      </div>

      {/* 탈락 사유별 Breakdown */}
      <div className="breakdown-section">
        <h3>탈락 사유별 상세 분석</h3>
        <ul className="breakdown-list">
          {rejected.salary > 0 && (
            <li className="breakdown-item">
              <span className="reason-icon">💰</span>
              <span className="reason-text">연봉 초과</span>
              <span className="reason-count">{rejected.salary}건</span>
            </li>
          )}
          {rejected.experience > 0 && (
            <li className="breakdown-item">
              <span className="reason-icon">📚</span>
              <span className="reason-text">경력 요구사항</span>
              <span className="reason-count">{rejected.experience}건</span>
            </li>
          )}
          {rejected.clearance > 0 && (
            <li className="breakdown-item">
              <span className="reason-icon">🔐</span>
              <span className="reason-text">보안 인가 필수</span>
              <span className="reason-count">{rejected.clearance}건</span>
            </li>
          )}
          {rejected.education > 0 && (
            <li className="breakdown-item">
              <span className="reason-icon">🎓</span>
              <span className="reason-text">학위 요구사항 (2:1)</span>
              <span className="reason-count">{rejected.education}건</span>
            </li>
          )}
          {rejected.level > 0 && (
            <li className="breakdown-item">
              <span className="reason-icon">👔</span>
              <span className="reason-text">직급 수준 (Lead/Principal)</span>
              <span className="reason-count">{rejected.level}건</span>
            </li>
          )}
        </ul>
      </div>

      {/* 시트 링크 버튼 */}
      {sheetUrl && (
        <div className="sheet-link-section">
          <a 
            href={sheetUrl} 
            target="_blank" 
            rel="noopener noreferrer"
            className="sheet-link-btn"
          >
            📊 Google Sheets에서 보기
          </a>
        </div>
      )}
    </div>
  )
}

export default ResultPanel
