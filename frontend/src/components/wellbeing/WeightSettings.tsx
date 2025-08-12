'use client';

import React, { useState, useEffect } from 'react';
import { WeightSlider } from '@/components/ui/WeightSlider';
import { useStore } from '@/store/useStore';
import { wellbeingApi } from '@/lib/api';
import { WellbeingWeights } from '@/types/area';

const weightCategories = [
  { key: 'rent', label: '家賃・住居費', icon: '🏠', color: 'blue' },
  { key: 'safety', label: '治安・安全性', icon: '🛡️', color: 'green' },
  { key: 'education', label: '教育環境', icon: '🎓', color: 'yellow' },
  { key: 'parks', label: '公園・緑地', icon: '🌳', color: 'green' },
  { key: 'medical', label: '医療・福祉', icon: '🏥', color: 'red' },
  { key: 'culture', label: '文化・施設', icon: '🎭', color: 'purple' },
] as const;

export const WeightSettings: React.FC = () => {
  const { weights, setWeights } = useStore();
  // weightsのデフォルト値を保証
  const safeWeights = {
    rent: weights.rent || 0.25,
    safety: weights.safety || 0.20,
    education: weights.education || 0.20,
    parks: weights.parks || 0.15,
    medical: weights.medical || 0.10,
    culture: weights.culture || 0.10,
  };
  const [localWeights, setLocalWeights] = useState(safeWeights);
  const [presets, setPresets] = useState<Record<string, any>>({});

  useEffect(() => {
    // プリセットを取得
    wellbeingApi.getWeightPresets().then(setPresets).catch(console.error);
  }, []);

  const handleWeightChange = (key: keyof WellbeingWeights, value: number) => {
    // 合計が1になるように調整
    const otherKeys = weightCategories
      .map((c) => c.key)
      .filter((k) => k !== key) as (keyof WellbeingWeights)[];
    
    const otherSum = otherKeys.reduce((sum, k) => sum + localWeights[k], 0);
    const maxValue = 1 - otherSum;
    const adjustedValue = Math.min(value, maxValue);

    setLocalWeights({
      ...localWeights,
      [key]: adjustedValue,
    });
  };

  const normalizeWeights = () => {
    const total = Object.values(localWeights).reduce((sum, v) => sum + v, 0);
    if (total === 0) return;

    const normalized = Object.entries(localWeights).reduce((acc, [key, value]) => {
      acc[key as keyof WellbeingWeights] = value / total;
      return acc;
    }, {} as WellbeingWeights);

    setLocalWeights(normalized);
  };

  const applyPreset = (presetKey: string) => {
    const preset = presets[presetKey];
    if (preset && preset.weights) {
      setLocalWeights(preset.weights);
    }
  };

  const applyWeights = () => {
    normalizeWeights();
    setWeights(localWeights);
  };

  const total = Object.values(localWeights).reduce((sum, v) => sum + v, 0);
  const isValid = Math.abs(total - 1) < 0.01;

  return (
    <div className="bg-white rounded-lg shadow p-6 space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">重要度の設定</h3>
        <p className="text-sm text-gray-600">
          各項目の重要度を調整してください（合計100%）
        </p>
      </div>

      {/* プリセット */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">プリセット</label>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(presets).map(([key, preset]) => (
            <button
              key={key}
              onClick={() => applyPreset(key)}
              className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors text-left"
            >
              <div className="font-medium">{preset.name}</div>
              <div className="text-xs text-gray-600">{preset.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* スライダー */}
      <div className="space-y-4">
        {weightCategories.map(({ key, label, icon, color }) => (
          <WeightSlider
            key={key}
            label={label}
            value={localWeights[key]}
            onChange={(value) => handleWeightChange(key, value)}
            icon={icon}
            color={color}
          />
        ))}
      </div>

      {/* 合計表示 */}
      <div className={`text-center p-3 rounded-md ${isValid ? 'bg-green-50' : 'bg-red-50'}`}>
        <p className={`text-sm font-medium ${isValid ? 'text-green-700' : 'text-red-700'}`}>
          合計: {Math.round(total * 100)}%
          {!isValid && ' (100%に調整してください)'}
        </p>
      </div>

      {/* ボタン */}
      <div className="flex gap-2">
        <button
          onClick={normalizeWeights}
          className="px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded-md hover:bg-gray-300 transition-colors"
        >
          自動調整
        </button>
        <button
          onClick={applyWeights}
          disabled={!isValid}
          className={`flex-1 px-4 py-2 font-medium rounded-md transition-colors ${
            isValid
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          適用
        </button>
      </div>
    </div>
  );
};