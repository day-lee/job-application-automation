import React, { useState, useRef } from 'react'
import { uploadFile } from '../api'

/**
 * FileUpload 컴포넌트
 * JSON 파일 선택/업로드 및 미리보기 표시
 */
function FileUpload({ onUploadSuccess, isLoading }) {
  const [uploadedJobCount, setUploadedJobCount] = useState(null)
  const [uploadError, setUploadError] = useState(null)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef(null)

  const handleFileSelect = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    // 파일 형식 검증 (프론트엔드)
    if (!file.name.endsWith('.json')) {
      setUploadError('❌ JSON 파일만 업로드 가능합니다')
      return
    }

    if (file.size === 0) {
      setUploadError('❌ 빈 파일입니다')
      return
    }

    setUploadError(null)
    setUploading(true)

    try {
      // 백엔드로 업로드
      const result = await uploadFile(file)
      
      setUploadedJobCount(result.jobCount)
      setUploadError(null)
      
      // 부모 컴포넌트에 알림
      if (onUploadSuccess) {
        onUploadSuccess(result)
      }
    } catch (error) {
      setUploadError(`❌ 업로드 실패: ${error.message}`)
      setUploadedJobCount(null)
    } finally {
      setUploading(false)
      // 다시 선택할 수 있도록 초기화
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  return (
    <div className="upload-section">
      <h2>📁 파일 업로드</h2>
      
      {/* 파일 선택 영역 */}
      <div className="file-input-wrapper">
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleFileSelect}
          disabled={isLoading || uploading}
          className="file-input"
          id="json-file-input"
        />
        <label htmlFor="json-file-input" className="file-label">
          {uploading ? '⏳ 업로드 중...' : '클릭하여 JSON 파일 선택'}
        </label>
      </div>

      {/* 업로드 결과 표시 */}
      {uploadedJobCount !== null && (
        <div className="upload-success">
          ✅ 업로드 성공: <strong>{uploadedJobCount}개의 채용공고</strong>가 준비되었습니다.
        </div>
      )}

      {/* 에러 표시 */}
      {uploadError && (
        <div className="upload-error">
          {uploadError}
        </div>
      )}
    </div>
  )
}

export default FileUpload
