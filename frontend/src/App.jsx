import React, { useState } from 'react'
import FileUpload from './components/FileUpload'
import FilterButton from './components/FilterButton'
import ResultPanel from './components/ResultPanel'
import { filterJobs } from './api'
import './styles/App.css'

/**
 * App 컴포넌트 - 메인 애플리케이션
 * 파일 업로드 -> 필터링 -> 결과 표시 플로우
 */
function App() {
  const [uploadedJobCount, setUploadedJobCount] = useState(null)
  const [isFilterLoading, setIsFilterLoading] = useState(false)
  const [filterResult, setFilterResult] = useState(null)
  const [filterError, setFilterError] = useState(null)

  const handleUploadSuccess = (uploadResult) => {
    setUploadedJobCount(uploadResult.jobCount)
    // 새 업로드 시 이전 결과 초기화
    setFilterResult(null)
    setFilterError(null)
  }

  const handleFilter = async () => {
    if (uploadedJobCount === null || uploadedJobCount === 0) {
      setFilterError('파일이 업로드되지 않았습니다.')
      return
    }

    setIsFilterLoading(true)
    setFilterError(null)
    setFilterResult(null)

    try {
      const result = await filterJobs()
      setFilterResult(result)
      setFilterError(null)
    } catch (error) {
      setFilterError(error.message)
      setFilterResult(null)
    } finally {
      setIsFilterLoading(false)
    }
  }

  return (
    <div className="app">
      {/* 헤더 */}
      <header className="app-header">
        <div className="header-content">
          <h1>🔗 LinkedIn 채용공고 필터링 자동화</h1>
          <p className="subtitle">
            JSON 파일 업로드 → 지능형 필터링 → Google Sheets 자동 저장
          </p>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="app-main">
        <div className="container">
          {/* 1. 파일 업로드 섹션 */}
          <FileUpload 
            onUploadSuccess={handleUploadSuccess}
            isLoading={isFilterLoading}
          />

          {/* 2. 필터링 버튼 섹션 */}
          <FilterButton 
            onFilter={handleFilter}
            isLoading={isFilterLoading}
            uploadedJobCount={uploadedJobCount}
          />

          {/* 3. 결과 표시 섹션 */}
          <ResultPanel 
            result={filterResult}
            error={filterError}
            isLoading={isFilterLoading}
          />
        </div>
      </main>

      {/* 푸터 */}
      <footer className="app-footer">
        <p>Apify Actor: https://console.apify.com/actors/hKByXkMQaC5Qt9UMN/input</p>
        <p>24 hours: https://www.linkedin.com/jobs/search?keywords=Junior%20Software%20Engineer%20Javascript&location=London%20Area%2C%20United%20Kingdom&geoId=90009496&f_E=1%2C2%2C3%2C4&f_PP=100495523%2C110652431&f_TPR=r86400&position=1&pageNum=0 </p>
        <p>7 days: https://www.linkedin.com/jobs/search?keywords=Junior%20Software%20Engineer%20Javascript&location=London%20Area%2C%20United%20Kingdom&geoId=90009496&f_E=1%2C2%2C3%2C4&f_TPR=r604800&f_PP=100495523%2C110652431&position=1&pageNum=0</p>
        <p>--------------------------------------------------------------------------------------------------------------------------------------------------------------</p>       
        <p>Backend API: http://localhost:8888 | Frontend: http://localhost:5178</p>
        <p> Junior Software Engineer Javascript/ filter: experience level, location </p>
      </footer>
    </div>
  )
}

export default App
