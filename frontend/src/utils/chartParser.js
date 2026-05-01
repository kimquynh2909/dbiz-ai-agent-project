/**
 * Chart Parser Utility
 * Detects and extracts chart data from AI response content
 */

/**
 * Check if a string is a valid chart JSON response
 * @param {string} content - Message content to check
 * @returns {boolean}
 */
export const isChartData = (content) => {
  if (!content || typeof content !== 'string') return false
  
  try {
    // Try to find JSON in the content
    const jsonMatch = extractJsonFromContent(content)
    if (!jsonMatch) return false
    
    const parsed = JSON.parse(jsonMatch)
    return parsed && parsed.type === 'chart' && parsed.data
  } catch {
    return false
  }
}

/**
 * Extract JSON object from content (handles markdown code blocks)
 * @param {string} content 
 * @returns {string|null}
 */
export const extractJsonFromContent = (content) => {
  if (!content) return null
  
  // First try to parse entire content as JSON
  const trimmed = content.trim()
  if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
    try {
      JSON.parse(trimmed)
      return trimmed
    } catch {}
  }
  
  // Try to find JSON in code blocks
  const codeBlockMatch = content.match(/```(?:json)?\s*([\s\S]*?)\s*```/i)
  if (codeBlockMatch && codeBlockMatch[1]) {
    const jsonContent = codeBlockMatch[1].trim()
    try {
      JSON.parse(jsonContent)
      return jsonContent
    } catch {}
  }
  
  // Try to find JSON object pattern in content
  const jsonMatch = content.match(/\{[\s\S]*"type"\s*:\s*"chart"[\s\S]*\}/m)
  if (jsonMatch) {
    try {
      JSON.parse(jsonMatch[0])
      return jsonMatch[0]
    } catch {}
  }
  
  return null
}

/**
 * Parse chart data from message content
 * @param {string} content - Message content
 * @returns {{ chartData: object, textMessage: string } | null}
 */
export const parseChartData = (content) => {
  if (!content || typeof content !== 'string') return null
  
  try {
    const jsonContent = extractJsonFromContent(content)
    if (!jsonContent) return null
    
    const parsed = JSON.parse(jsonContent)
    if (parsed.type !== 'chart' || !parsed.data) return null
    
    return {
      chartData: {
        chartType: parsed.chart_type || 'bar',
        title: parsed.title || '',
        data: parsed.data,
        options: parsed.options || {},
        summary: parsed.summary || null
      },
      textMessage: parsed.message || ''
    }
  } catch (e) {
    console.error('Failed to parse chart data:', e)
    return null
  }
}

/**
 * Format the text message that accompanies the chart
 * @param {string} message - The text message from chart data
 * @returns {string}
 */
export const formatChartMessage = (message) => {
  if (!message) return ''
  
  // Convert markdown-like formatting to simple HTML
  return message
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>')
}

export default {
  isChartData,
  parseChartData,
  extractJsonFromContent,
  formatChartMessage
}

