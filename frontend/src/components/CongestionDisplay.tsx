'use client'

import React from 'react'

interface CongestionLevel {
  level: string
  label: string
  color: string
  description: string
}

interface CongestionData {
  overall: {
    score: number
    level: CongestionLevel
  }
  time_based: {
    weekday: number
    weekend: number
    morning: number
    daytime: number
    evening: number
  }
  facility_based: {
    station: number
    shopping: number
    park: number
    residential: number
  }
  family_metrics: {
    family_friendliness: number
    stroller_accessibility: number
    quiet_area_ratio: number
  }
}

interface CongestionDisplayProps {
  congestion: CongestionData
}

const CongestionDisplay: React.FC<CongestionDisplayProps> = ({ congestion }) => {
  // データの存在チェック
  if (!congestion || !congestion.overall) {
    return (
      <div className="bg-gray-100 rounded-lg p-6 text-center">
        <p className="text-gray-500">混雑度情報は現在利用できません</p>
      </div>
    )
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#FF4444'
    if (score >= 60) return '#FF8800'
    if (score >= 40) return '#FFAA00'
    if (score >= 20) return '#88CC00'
    return '#00CC00'
  }

  const renderProgressBar = (score: number, label: string) => (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span>{label}</span>
        <span>{Math.round(score)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="h-2 rounded-full transition-all duration-300"
          style={{ 
            width: `${score}%`,
            backgroundColor: getScoreColor(score)
          }}
        />
      </div>
    </div>
  )

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">🚶 混雑度情報</h3>
      
      {/* 総合混雑度 */}
      <div className="mb-6 p-4 rounded-lg" style={{ backgroundColor: congestion.overall.level.color + '20' }}>
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-md font-medium">総合混雑度</h4>
          <span 
            className="px-3 py-1 rounded-full text-white text-sm font-medium"
            style={{ backgroundColor: congestion.overall.level.color }}
          >
            {congestion.overall.level.label}
          </span>
        </div>
        <p className="text-sm text-gray-600">{congestion.overall.level.description}</p>
        <div className="mt-2 text-2xl font-bold" style={{ color: congestion.overall.level.color }}>
          {Math.round(congestion.overall.score)}点
        </div>
      </div>

      {/* 時間帯別混雑度 */}
      <div className="mb-6">
        <h4 className="text-md font-medium mb-3">時間帯別混雑度</h4>
        {renderProgressBar(congestion.time_based.morning, '朝（7-9時）')}
        {renderProgressBar(congestion.time_based.daytime, '昼間（10-16時）')}
        {renderProgressBar(congestion.time_based.evening, '夕方（17-19時）')}
        {renderProgressBar(congestion.time_based.weekday, '平日')}
        {renderProgressBar(congestion.time_based.weekend, '週末')}
      </div>

      {/* 施設タイプ別混雑度 */}
      <div className="mb-6">
        <h4 className="text-md font-medium mb-3">施設タイプ別混雑度</h4>
        {renderProgressBar(congestion.facility_based.station, '駅周辺')}
        {renderProgressBar(congestion.facility_based.shopping, '商業施設')}
        {renderProgressBar(congestion.facility_based.park, '公園')}
        {renderProgressBar(congestion.facility_based.residential, '住宅地')}
      </div>

      {/* ファミリー向け指標 */}
      <div className="bg-blue-50 rounded-lg p-4">
        <h4 className="text-md font-medium mb-3">👨‍👩‍👧‍👦 ファミリー向け指標</h4>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-sm">子育て環境スコア</span>
            <span className="text-sm font-medium">
              {Math.round(congestion.family_metrics.family_friendliness)}点
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm">ベビーカーアクセシビリティ</span>
            <span className="text-sm font-medium">
              {Math.round(congestion.family_metrics.stroller_accessibility)}%
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm">静かなエリアの割合</span>
            <span className="text-sm font-medium">
              {Math.round(congestion.family_metrics.quiet_area_ratio)}%
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CongestionDisplay