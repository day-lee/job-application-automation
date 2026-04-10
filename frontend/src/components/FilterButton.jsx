import React from 'react'

/**
 * FilterButton 컴포넌트
 * 필터링 시작 버튼 및 로딩 표시
 */
function FilterButton({ onFilter, isLoading, uploadedJobCount }) {
  const handleClick = () => {
    if (uploadedJobCount === null || uploadedJobCount === 0) {
      alert('먼저 JSON 파일을 업로드해주세요.')
      return
    }
    onFilter()
  }

  return (
    <div className="filter-section">
      <button 
        className="filter-btn"
        onClick={handleClick}
        disabled={isLoading}
      >
        {isLoading ? (
          <>
            <span className="spinner"></span>
            필터링 중...
          </>
        ) : (
          '🚀 필터링 시작'
        )}
      </button>

      {isLoading && (
        <p className="filter-status">
          채용공고를 필터링하고 있습니다. 잠시 기다려주세요...
        </p>
      )}
    </div>
  )
}

export default FilterButton
