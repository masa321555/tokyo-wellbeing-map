import React from 'react';
import { WasteSeparation } from '@/types/area';

interface WasteSeparationDisplayProps {
  data: WasteSeparation;
}

export default function WasteSeparationDisplay({ data }: WasteSeparationDisplayProps) {
  const getStrictnessLevel = (level?: number) => {
    if (!level) return '標準';
    if (level <= 2) return '緩やか';
    if (level <= 3) return '標準';
    if (level <= 4) return 'やや厳しい';
    return '厳しい';
  };

  const getStrictnessColor = (level?: number) => {
    if (!level) return 'text-gray-600';
    if (level <= 2) return 'text-green-600';
    if (level <= 3) return 'text-blue-600';
    if (level <= 4) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">♻️ ゴミ分別ルール</h3>
      
      {/* 分別の厳しさレベル */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-600">分別の厳しさ</span>
          <span className={`font-medium ${getStrictnessColor(data.strictness_level)}`}>
            {getStrictnessLevel(data.strictness_level)}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="h-2 rounded-full bg-gradient-to-r from-green-400 via-yellow-400 to-red-400"
            style={{ width: `${(data.strictness_level || 3) * 20}%` }}
          />
        </div>
      </div>

      {/* 分別カテゴリ */}
      {data.separation_types && data.separation_types.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">分別カテゴリ</h4>
          <div className="flex flex-wrap gap-2">
            {data.separation_types.map((type, index) => (
              <span 
                key={index}
                className="px-2 py-1 bg-gray-100 text-gray-700 text-sm rounded"
              >
                {type}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* 収集曜日 */}
      {data.collection_days && Object.keys(data.collection_days).length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">収集曜日</h4>
          <dl className="space-y-1">
            {Object.entries(data.collection_days).map(([type, days]) => (
              <div key={type} className="flex justify-between text-sm">
                <dt className="text-gray-600">{type}</dt>
                <dd className="font-medium">{days}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {/* 特別なルール */}
      {data.special_rules && data.special_rules.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">特別なルール</h4>
          <ul className="list-disc list-inside space-y-1">
            {data.special_rules.map((rule, index) => (
              <li key={index} className="text-sm text-gray-600">
                {rule}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 特徴 */}
      {data.features && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">特徴</h4>
          <p className="text-sm text-gray-600">{data.features}</p>
        </div>
      )}

      {/* データソース */}
      {data.data_source && (
        <div className="text-xs text-gray-500 mt-4 pt-4 border-t">
          出典: {data.data_source}
        </div>
      )}
    </div>
  );
}