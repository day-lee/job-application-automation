/**
 * 백엔드 API 통신 모듈
 * 모든 API 요청 (upload, filter)을 처리
 */

const API_BASE_URL = 'http://localhost:8888'

/**
 * 파일 업로드
 * @param {File} file - 업로드할 JSON 파일
 * @returns {Promise<{filename: string, jobCount: number}>}
 */
export const uploadFile = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail?.error || 'File upload failed')
    }

    return await response.json()
  } catch (error) {
    throw error
  }
}

/**
 * 필터링 실행
 * @returns {Promise<{
 *   success: boolean,
 *   total: number,
 *   duplicatesRemoved: number,
 *   passed: number,
 *   filtered: number,
 *   savedToSheet: number,
 *   rejected: {salary:number, experience:number, clearance:number, education:number, level:number, stack:number},
 *   sheetUrl: string,
 *   message: string
 * }>}
 */
export const filterJobs = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/filter`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail?.error || 'Filtering failed')
    }

    return await response.json()
  } catch (error) {
    throw error
  }
}

/**
 * 헬스 체크
 * @returns {Promise<{status: string}>}
 */
export const healthCheck = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`)
    if (!response.ok) throw new Error('Health check failed')
    return await response.json()
  } catch (error) {
    throw error
  }
}
