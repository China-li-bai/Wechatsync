export function evaluateRewriteQuality(originalText, rewrittenText) {
  if (!originalText || !rewrittenText) {
    return {
      overallScore: 0,
      details: {
        semanticFidelity: 0,
        expressionDiversity: 0,
        humanCharacteristics: 0,
        antiDetectionScore: 0
      },
      suggestions: ['原文或改写文本为空']
    }
  }

  const details = {
    semanticFidelity: evaluateSemanticFidelity(originalText, rewrittenText),
    expressionDiversity: evaluateExpressionDiversity(rewrittenText),
    humanCharacteristics: evaluateHumanCharacteristics(rewrittenText),
    antiDetectionScore: evaluateAntiDetection(rewrittenText)
  }

  const overallScore = Math.round(
    (details.semanticFidelity + 
     details.expressionDiversity + 
     details.humanCharacteristics + 
     details.antiDetectionScore) / 4
  )

  const suggestions = generateSuggestions(details)

  return {
    overallScore,
    details,
    suggestions,
    grade: getGrade(overallScore)
  }
}

function evaluateSemanticFidelity(originalText, rewrittenText) {
  let score = 100
  
  const originalKeywords = extractKeywords(originalText)
  const rewrittenKeywords = extractKeywords(rewrittenText)
  
  const commonKeywords = originalKeywords.filter(k => rewrittenKeywords.includes(k))
  const keywordRetentionRate = commonKeywords.length / Math.max(originalKeywords.length, 1)
  
  if (keywordRetentionRate < 0.5) {
    score -= 30
  } else if (keywordRetentionRate < 0.7) {
    score -= 15
  }
  
  const originalLength = originalText.length
  const rewrittenLength = rewrittenText.length
  const lengthRatio = rewrittenLength / originalLength
  
  if (lengthRatio < 0.5 || lengthRatio > 2.0) {
    score -= 20
  } else if (lengthRatio < 0.7 || lengthRatio > 1.5) {
    score -= 10
  }
  
  const originalSentences = splitSentences(originalText)
  const rewrittenSentences = splitSentences(rewrittenText)
  
  if (Math.abs(originalSentences.length - rewrittenSentences.length) > originalSentences.length * 0.5) {
    score -= 15
  }
  
  return Math.max(0, Math.min(100, score))
}

function evaluateExpressionDiversity(text) {
  let score = 100
  
  const sentences = splitSentences(text)
  if (sentences.length === 0) return 0
  
  const sentenceStructures = sentences.map(s => analyzeSentenceStructure(s))
  const uniqueStructures = new Set(sentenceStructures)
  const structureDiversity = uniqueStructures.size / sentenceStructures.length
  
  if (structureDiversity < 0.3) {
    score -= 40
  } else if (structureDiversity < 0.5) {
    score -= 20
  } else if (structureDiversity < 0.7) {
    score -= 10
  }
  
  const words = text.split(/\s+/).filter(w => w.length > 0)
  const uniqueWords = new Set(words.map(w => w.toLowerCase()))
  const vocabularyDiversity = uniqueWords.size / Math.max(words.length, 1)
  
  if (vocabularyDiversity < 0.3) {
    score -= 30
  } else if (vocabularyDiversity < 0.5) {
    score -= 15
  }
  
  const sentenceLengths = sentences.map(s => s.length)
  const avgLength = sentenceLengths.reduce((a, b) => a + b, 0) / sentenceLengths.length
  const lengthVariance = sentenceLengths.reduce((sum, len) => sum + Math.pow(len - avgLength, 2), 0) / sentenceLengths.length
  
  if (lengthVariance < 100) {
    score -= 20
  } else if (lengthVariance < 300) {
    score -= 10
  }
  
  return Math.max(0, Math.min(100, score))
}

function evaluateHumanCharacteristics(text) {
  let score = 100
  
  const humanPatterns = [
    /\？/g,
    /\！/g,
    /\.\.\./g,
    /——/g,
    /\（[^）]+\）/g,
    /\[[^\]]+\]/g,
    /比如|例如|举个例子|以.*为例/g,
    /我认为|我觉得|在我看来|个人认为/g,
    /其实|实际上|事实上/g,
    /当然|不过|然而|但是/g
  ]
  
  let humanPatternCount = 0
  humanPatterns.forEach(pattern => {
    const matches = text.match(pattern)
    if (matches) {
      humanPatternCount += matches.length
    }
  })
  
  const sentences = splitSentences(text)
  const humanPatternDensity = humanPatternCount / Math.max(sentences.length, 1)
  
  if (humanPatternDensity < 0.2) {
    score -= 30
  } else if (humanPatternDensity < 0.5) {
    score -= 15
  } else if (humanPatternDensity > 1.5) {
    score += 10
  }
  
  const aiPatterns = [
    /随着.*的发展/g,
    /在.*背景下/g,
    /显著提升/g,
    /具有重要意义/g,
    /综上所述/g,
    /总而言之/g,
    /首先.*其次.*最后/g
  ]
  
  let aiPatternCount = 0
  aiPatterns.forEach(pattern => {
    const matches = text.match(pattern)
    if (matches) {
      aiPatternCount += matches.length
    }
  })
  
  if (aiPatternCount > 3) {
    score -= 30
  } else if (aiPatternCount > 1) {
    score -= 15
  }
  
  const passiveVoicePattern = /被|由|受到|得到/g
  const passiveMatches = text.match(passiveVoicePattern)
  const passiveDensity = passiveMatches ? passiveMatches.length / text.length : 0
  
  if (passiveDensity > 0.02) {
    score += 10
  }
  
  return Math.max(0, Math.min(100, score))
}

function evaluateAntiDetection(text) {
  let score = 100
  
  const aiHighFreqPatterns = [
    /非常|极其|相当|十分/g,
    /重要|关键|核心/g,
    /发展|进步|提升/g,
    /影响|作用|意义/g,
    /问题|挑战|机遇/g
  ]
  
  let aiHighFreqCount = 0
  aiHighFreqPatterns.forEach(pattern => {
    const matches = text.match(pattern)
    if (matches) {
      aiHighFreqCount += matches.length
    }
  })
  
  const textLength = text.length
  const aiHighFreqDensity = aiHighFreqCount / textLength
  
  if (aiHighFreqDensity > 0.01) {
    score -= 30
  } else if (aiHighFreqDensity > 0.005) {
    score -= 15
  }
  
  const specificDataPatterns = [
    /\d+%/g,
    /\d+年/g,
    /\d+月/g,
    /\d+日/g,
    /\d+亿/g,
    /\d+万/g,
    /根据.*调查/g,
    /据.*统计/g,
    /数据显示/g
  ]
  
  let specificDataCount = 0
  specificDataPatterns.forEach(pattern => {
    const matches = text.match(pattern)
    if (matches) {
      specificDataCount += matches.length
    }
  })
  
  if (specificDataCount > 3) {
    score += 20
  } else if (specificDataCount > 1) {
    score += 10
  }
  
  const sentences = splitSentences(text)
  const sentenceStructures = sentences.map(s => analyzeSentenceStructure(s))
  const uniqueStructures = new Set(sentenceStructures)
  
  if (uniqueStructures.size < sentences.length * 0.5) {
    score -= 20
  }
  
  const transitionWords = ['但是', '然而', '不过', '其实', '实际上', '当然', '因此', '所以', '那么', '于是']
  let transitionCount = 0
  transitionWords.forEach(word => {
    if (text.includes(word)) {
      transitionCount++
    }
  })
  
  if (transitionCount > 2) {
    score += 10
  }
  
  return Math.max(0, Math.min(100, score))
}

function extractKeywords(text) {
  const stopWords = new Set(['的', '了', '和', '是', '在', '有', '我', '他', '她', '它', '这', '那', '就', '也', '都', '而', '及', '与', '或', '但', '如', '等', '被', '把', '给', '让', '向', '从', '对', '为', '以', '于', '上', '下', '中', '里', '外', '前', '后', '左', '右'])
  
  const words = text.split(/[\s，。！？、；：""''（）【】《》\n]+/)
  const keywords = words
    .filter(w => w.length >= 2 && !stopWords.has(w))
    .map(w => w.toLowerCase())
  
  return [...new Set(keywords)]
}

function splitSentences(text) {
  return text.split(/[。！？\n]+/).filter(s => s.trim().length > 0)
}

function analyzeSentenceStructure(sentence) {
  const hasQuestion = sentence.includes('？') || sentence.includes('?')
  const hasExclamation = sentence.includes('！') || sentence.includes('!')
  const hasParentheses = sentence.includes('（') || sentence.includes('(')
  const hasQuotes = sentence.includes('"') || sentence.includes('"')
  
  const length = sentence.length
  const lengthCategory = length < 10 ? 'short' : length < 30 ? 'medium' : 'long'
  
  return `${lengthCategory}-${hasQuestion}-${hasExclamation}-${hasParentheses}-${hasQuotes}`
}

function generateSuggestions(details) {
  const suggestions = []
  
  if (details.semanticFidelity < 70) {
    suggestions.push('语义保真度较低，建议检查是否保留了原文的核心信息')
  }
  
  if (details.expressionDiversity < 70) {
    suggestions.push('表达多样性不足，建议增加句式变化和词汇丰富度')
  }
  
  if (details.humanCharacteristics < 70) {
    suggestions.push('人类特征不明显，建议加入更多口语化表达、个人见解或具体案例')
  }
  
  if (details.antiDetectionScore < 70) {
    suggestions.push('AI检测规避度较低，建议使用"深度改写"模式或手动添加具体数据、地域特色')
  }
  
  if (suggestions.length === 0) {
    suggestions.push('改写质量优秀！建议进行最终人工审核后发布')
  }
  
  return suggestions
}

function getGrade(score) {
  if (score >= 90) return { level: '优秀', color: '#67c23a', emoji: '🌟' }
  if (score >= 80) return { level: '良好', color: '#409eff', emoji: '✨' }
  if (score >= 70) return { level: '合格', color: '#e6a23c', emoji: '👍' }
  return { level: '需改进', color: '#f56c6c', emoji: '⚠️' }
}

export function getRewriteModeDescription(mode) {
  const descriptions = {
    academic: '高级学术语言，句式多样，避免AI痕迹',
    human_rhythm: '模仿人类写作节奏，口语化表达',
    logic_restructure: '改变论证顺序，打破线性逻辑',
    sentence_restructure: '逐句改变句式结构，降低重复率',
    keyword_replace: '换词不换义，插入注释和举例',
    anti_detection: '综合所有规避策略，AI检测率可降至10%以下'
  }
  
  return descriptions[mode] || '标准改写模式'
}

export function getRecommendedMode(textType) {
  const recommendations = {
    academic: 'academic',
    blog: 'human_rhythm',
    news: 'logic_restructure',
    technical: 'keyword_replace',
    social: 'human_rhythm',
    default: 'anti_detection'
  }
  
  return recommendations[textType] || recommendations.default
}
