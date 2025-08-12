'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { wellbeingApi } from '@/lib/api';
import { AreaCard } from '@/components/ui/AreaCard';
import { Lightbulb, Filter, Star, TrendingUp, Home, Users, DollarSign, Shield, School, Trees, Stethoscope, Building } from 'lucide-react';

interface UserProfile {
  preferences: {
    rent: number;
    safety: number;
    education: number;
    parks: number;
    medical: number;
    culture: number;
  };
  constraints: {
    max_rent?: number;
    min_parks?: number;
    no_waiting_children?: boolean;
    min_elementary_schools?: number;
    max_crime_rate?: number;
  };
}

interface Recommendation {
  area_id: number;
  area_name: string;
  total_score: number;
  category_scores: Record<string, number>;
  match_reasons: string[];
}

export default function RecommendationsPage() {
  const router = useRouter();
  const [userProfile, setUserProfile] = useState<UserProfile>({
    preferences: {
      rent: 0.25,
      safety: 0.20,
      education: 0.20,
      parks: 0.15,
      medical: 0.10,
      culture: 0.10
    },
    constraints: {}
  });
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(true);
  const [presetProfiles, setPresetProfiles] = useState<any>(null);

  useEffect(() => {
    loadPresetProfiles();
  }, []);

  const loadPresetProfiles = async () => {
    try {
      const presets = await wellbeingApi.getWeightPresets();
      setPresetProfiles(presets);
    } catch (error) {
      console.error('Failed to load presets:', error);
    }
  };

  const loadRecommendations = async () => {
    setLoading(true);
    try {
      const result = await wellbeingApi.getRecommendations(
        userProfile.preferences,
        userProfile.constraints
      );
      setRecommendations(result.recommendations);
      setShowSettings(false);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const updatePreference = (key: string, value: number) => {
    const newPreferences = { ...userProfile.preferences, [key]: value };
    
    // 合計が1になるように調整
    const total = Object.values(newPreferences).reduce((sum, v) => sum + v, 0);
    if (total !== 1) {
      const scale = 1 / total;
      Object.keys(newPreferences).forEach(k => {
        newPreferences[k as keyof typeof newPreferences] *= scale;
      });
    }
    
    setUserProfile({
      ...userProfile,
      preferences: newPreferences
    });
  };

  const updateConstraint = (key: string, value: any) => {
    const newConstraints = { ...userProfile.constraints };
    if (value === '' || value === null || value === undefined) {
      delete newConstraints[key as keyof typeof newConstraints];
    } else {
      newConstraints[key as keyof typeof newConstraints] = value;
    }
    setUserProfile({
      ...userProfile,
      constraints: newConstraints
    });
  };

  const applyPreset = (preset: any) => {
    setUserProfile({
      ...userProfile,
      preferences: preset.weights
    });
  };

  const getIcon = (category: string) => {
    const icons: Record<string, React.ReactElement> = {
      rent: <DollarSign className="w-5 h-5" />,
      safety: <Shield className="w-5 h-5" />,
      education: <School className="w-5 h-5" />,
      parks: <Trees className="w-5 h-5" />,
      medical: <Stethoscope className="w-5 h-5" />,
      culture: <Building className="w-5 h-5" />
    };
    return icons[category] || null;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <Lightbulb className="w-8 h-8 text-yellow-500" />
          エリア推薦機能
        </h1>
        <p className="text-gray-600">
          あなたの好みに合わせて、最適なエリアをAIが推薦します
        </p>
      </div>

      {showSettings && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Filter className="w-5 h-5" />
            あなたの優先順位を設定
          </h2>

          {/* プリセット選択 */}
          {presetProfiles && (
            <div className="mb-6">
              <p className="text-sm text-gray-600 mb-3">プリセットから選択：</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {Object.entries(presetProfiles).map(([key, preset]: any) => (
                  <button
                    key={key}
                    onClick={() => applyPreset(preset)}
                    className="p-3 border rounded-lg hover:bg-gray-50 transition-colors text-left"
                  >
                    <div className="font-medium text-sm">{preset.name}</div>
                    <div className="text-xs text-gray-500">{preset.description}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 重要度スライダー */}
          <div className="space-y-4 mb-6">
            <p className="text-sm text-gray-600">各要素の重要度を設定：</p>
            {Object.entries(userProfile.preferences).map(([key, value]) => (
              <div key={key} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getIcon(key)}
                    <span className="font-medium">
                      {key === 'rent' && '家賃'}
                      {key === 'safety' && '治安'}
                      {key === 'education' && '教育'}
                      {key === 'parks' && '公園'}
                      {key === 'medical' && '医療'}
                      {key === 'culture' && '文化'}
                    </span>
                  </div>
                  <span className="text-sm text-gray-600">
                    {(value * 100).toFixed(0)}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={value * 100}
                  onChange={(e) => updatePreference(key, Number(e.target.value) / 100)}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
            ))}
          </div>

          {/* 制約条件 */}
          <div className="border-t pt-6">
            <h3 className="font-medium mb-4">必須条件（オプション）</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  最大家賃（万円）
                </label>
                <input
                  type="number"
                  placeholder="例: 20"
                  value={userProfile.constraints.max_rent || ''}
                  onChange={(e) => updateConstraint('max_rent', e.target.value ? Number(e.target.value) : null)}
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  最小公園数
                </label>
                <input
                  type="number"
                  placeholder="例: 10"
                  value={userProfile.constraints.min_parks || ''}
                  onChange={(e) => updateConstraint('min_parks', e.target.value ? Number(e.target.value) : null)}
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  最小小学校数
                </label>
                <input
                  type="number"
                  placeholder="例: 5"
                  value={userProfile.constraints.min_elementary_schools || ''}
                  onChange={(e) => updateConstraint('min_elementary_schools', e.target.value ? Number(e.target.value) : null)}
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  最大犯罪率（件/千人）
                </label>
                <input
                  type="number"
                  step="0.1"
                  placeholder="例: 5.0"
                  value={userProfile.constraints.max_crime_rate || ''}
                  onChange={(e) => updateConstraint('max_crime_rate', e.target.value ? Number(e.target.value) : null)}
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>
            </div>
            <div className="mt-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={userProfile.constraints.no_waiting_children || false}
                  onChange={(e) => updateConstraint('no_waiting_children', e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm font-medium text-gray-700">
                  待機児童ゼロのエリアのみ
                </span>
              </label>
            </div>
          </div>

          {/* 推薦取得ボタン */}
          <div className="mt-6 flex justify-center">
            <button
              onClick={loadRecommendations}
              disabled={loading}
              className="px-8 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <TrendingUp className="w-5 h-5" />
              {loading ? '推薦を生成中...' : 'あなたにおすすめのエリアを見る'}
            </button>
          </div>
        </div>
      )}

      {/* 推薦結果 */}
      {!showSettings && recommendations.length > 0 && (
        <>
          <div className="mb-6 flex justify-between items-center">
            <h2 className="text-2xl font-semibold">あなたにおすすめのエリア</h2>
            <button
              onClick={() => setShowSettings(true)}
              className="px-4 py-2 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50 transition-colors"
            >
              条件を変更
            </button>
          </div>

          <div className="space-y-6">
            {recommendations.map((rec, index) => (
              <div key={rec.area_id} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
                    {index + 1}
                  </div>
                  <div className="flex-grow">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-xl font-semibold">{rec.area_name}</h3>
                      <div className="flex items-center gap-1 text-yellow-500">
                        <Star className="w-5 h-5 fill-current" />
                        <span className="font-medium">{rec.total_score.toFixed(1)}</span>
                      </div>
                    </div>

                    {/* マッチ理由 */}
                    <div className="mb-4">
                      <p className="text-sm text-gray-600 mb-2">おすすめの理由：</p>
                      <ul className="space-y-1">
                        {rec.match_reasons.map((reason, idx) => (
                          <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                            <span className="text-green-500 mt-1">✓</span>
                            <span>{reason}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* カテゴリスコア */}
                    <div className="grid grid-cols-3 md:grid-cols-6 gap-3 mb-4">
                      {Object.entries(rec.category_scores).map(([category, score]) => (
                        <div key={category} className="text-center">
                          <div className="flex justify-center mb-1">
                            {getIcon(category)}
                          </div>
                          <div className="text-xs text-gray-600">
                            {category === 'rent' && '家賃'}
                            {category === 'safety' && '治安'}
                            {category === 'education' && '教育'}
                            {category === 'parks' && '公園'}
                            {category === 'medical' && '医療'}
                            {category === 'culture' && '文化'}
                          </div>
                          <div className="text-sm font-medium">
                            {score.toFixed(0)}
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* アクションボタン */}
                    <div className="flex gap-3">
                      <button
                        onClick={() => router.push(`/areas/${rec.area_id}`)}
                        className="px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
                      >
                        詳細を見る
                      </button>
                      <button
                        onClick={() => window.open(`https://www.google.com/maps/search/${rec.area_name}+東京`, '_blank')}
                        className="px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-md hover:bg-gray-50 transition-colors"
                      >
                        地図で見る
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* ホームに戻るボタン */}
          <div className="mt-8 flex justify-center">
            <button
              onClick={() => router.push('/')}
              className="px-6 py-3 bg-gray-200 text-gray-700 font-medium rounded-md hover:bg-gray-300 transition-colors flex items-center gap-2"
            >
              <Home className="w-5 h-5" />
              ホームに戻る
            </button>
          </div>
        </>
      )}
    </div>
  );
}