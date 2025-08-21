import React from 'react';
import { WasteSeparation } from '@/types/area';

interface WasteSeparationContentProps {
  data: WasteSeparation;
}

export default function WasteSeparationContent({ data }: WasteSeparationContentProps) {
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
    <div>
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
                className="px-3 py-1 bg-gray-100 rounded-full text-sm text-gray-700"
              >
                {type}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* 収集日 */}
      {data.collection_days && Object.keys(data.collection_days).length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">収集日</h4>
          <div className="space-y-1">
            {Object.entries(data.collection_days).map(([type, days]) => (
              <div key={type} className="flex justify-between text-sm">
                <span className="text-gray-600">{type}</span>
                <span className="font-medium">{days}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 特別ルール */}
      {data.special_rules && data.special_rules.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">特別ルール</h4>
          <ul className="list-disc list-inside space-y-1">
            {data.special_rules.map((rule, index) => (
              <li key={index} className="text-sm text-gray-600">{rule}</li>
            ))}
          </ul>
        </div>
      )}

      {/* 特徴 */}
      {data.features && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">このエリアの特徴</h4>
          <p className="text-sm text-gray-600">{data.features}</p>
        </div>
      )}

      {/* 詳細情報 */}
      {data.item_details && Object.keys(data.item_details).length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">分別の詳細</h4>
          <div className="bg-gray-50 rounded-lg p-3 space-y-2">
            {Object.entries(data.item_details).map(([item, category]) => (
              <div key={item} className="flex justify-between text-sm">
                <span className="text-gray-600">{item}</span>
                <span className="font-medium text-gray-800">{category}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}