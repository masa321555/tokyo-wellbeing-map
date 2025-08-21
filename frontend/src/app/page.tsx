'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AreaCard } from '@/components/ui/AreaCard';
import { WeightSettings } from '@/components/wellbeing/WeightSettings';
import { SearchFilters } from '@/components/search/SearchFilters';
import { useStore } from '@/store/useStore';
import { areaApi, searchApi, wellbeingApi } from '@/lib/api';
import { Area } from '@/types/area';

export default function Home() {
  const router = useRouter();
  const { selectedAreas, addSelectedArea, weights, searchParams } = useStore();
  const [areas, setAreas] = useState<Area[]>([]);
  const [loading, setLoading] = useState(true);
  const [ranking, setRanking] = useState<any[]>([]);
  const [activeView, setActiveView] = useState<'search' | 'ranking'>('ranking');

  // 初期データ取得
  useEffect(() => {
    loadAreas();
  }, [searchParams]);

  // ランキング取得
  useEffect(() => {
    if (activeView === 'ranking') {
      loadRanking();
    }
  }, [weights, activeView]);

  const loadAreas = async () => {
    setLoading(true);
    try {
      if (Object.keys(searchParams).length > 0) {
        // 検索条件がある場合
        const result = await searchApi.searchAreas({
          ...searchParams,
          limit: 50,
        });
        setAreas(result.areas);
      } else {
        // 全エリア取得
        const allAreas = await areaApi.getAreas();
        setAreas(allAreas);
      }
    } catch (error) {
      console.error('Failed to load areas:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRanking = async () => {
    try {
      const result = await wellbeingApi.getRanking(weights, undefined, 23);
      setRanking(result.ranking);
    } catch (error) {
      console.error('Failed to load ranking:', error);
    }
  };

  const handleAreaClick = (area: Area) => {
    console.log('Area clicked:', area);
    addSelectedArea(area);
  };

  const handleViewDetail = (areaId: string) => {
    window.location.href = `/areas/${areaId}`;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      {/* ヘッダーセクション */}
      <div className="mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              あなたの理想の居住地を見つけよう
            </h1>
            <p className="text-gray-600">
              東京都内の各エリアを、あなたの価値観に基づいて評価・比較できます
            </p>
          </div>
          <button
            onClick={() => router.push('/recommendations')}
            className="px-4 py-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-white font-medium rounded-md hover:from-yellow-500 hover:to-orange-600 transition-all shadow-md flex items-center gap-2"
          >
            <span>✨</span>
            AIおすすめ
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* 左サイドバー */}
        <div className="lg:col-span-1 space-y-6">
          {/* タブ切り替え */}
          <div className="bg-white rounded-lg shadow p-1">
            <div className="grid grid-cols-2 gap-1">
              <button
                onClick={() => setActiveView('ranking')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeView === 'ranking'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                マッチング
              </button>
              <button
                onClick={() => setActiveView('search')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeView === 'search'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                条件検索
              </button>
            </div>
          </div>

          {/* 条件設定 */}
          {activeView === 'search' ? (
            <SearchFilters />
          ) : (
            <WeightSettings />
          )}

          {/* 選択中のエリア */}
          {selectedAreas.length > 0 && (
            <div className="bg-white rounded-lg shadow p-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-2">
                選択中のエリア ({selectedAreas.length})
              </h3>
              <div className="space-y-2">
                {selectedAreas.map((area) => (
                  <div key={area.id} className="text-sm text-gray-700">
                    {area.name}
                  </div>
                ))}
              </div>
              <button
                onClick={() => router.push('/compare')}
                className="mt-3 w-full px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
              >
                比較する
              </button>
            </div>
          )}
        </div>

        {/* メインコンテンツ */}
        <div className="lg:col-span-3">
          {/* 結果表示ヘッダー */}
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              {activeView === 'search' ? '検索結果' : 'エリアマッチング'}
              {areas.length > 0 && ` (${areas.length}件)`}
            </h2>
          </div>

          {/* マッチング結果の説明 */}
          {activeView === 'ranking' && ranking.length > 0 && (
            <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm text-blue-800">
                <span className="font-semibold">マッチング結果について：</span>
                あなたが設定した重要度（
                家賃・住居費: {Math.round(weights.rent * 100)}%、
                治安・安全性: {Math.round(weights.safety * 100)}%、
                教育環境: {Math.round(weights.education * 100)}%、
                公園・緑地: {Math.round(weights.parks * 100)}%、
                医療・福祉: {Math.round(weights.medical * 100)}%、
                文化・施設: {Math.round(weights.culture * 100)}%
                ）に基づいて、各エリアのスコアを算出しています。
                スコアが高いほど、あなたの価値観に合った地域です。
              </p>
            </div>
          )}

          {/* コンテンツ表示 */}
          {loading ? (
            <div className="flex items-center justify-center h-96">
              <div className="text-gray-500">データを読み込み中...</div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {activeView === 'search' ? (
                areas.map((area) => (
                  <AreaCard
                    key={area.id}
                    area={area}
                    isSelected={selectedAreas.some(a => a.id === area.id)}
                    onSelect={() => handleAreaClick(area)}
                    onViewDetail={() => handleViewDetail(area.id)}
                  />
                ))
              ) : (
                ranking.map((item, index) => (
                  <div key={item.area_id} className="relative">
                    <div className="absolute -top-2 -left-2 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                      {index + 1}
                    </div>
                    <AreaCard
                      area={{
                        id: item.area_id,
                        code: item.area_code,
                        name: item.area_name,
                        area_name: item.area_name,
                        wellbeing_score: item.total_score,
                        total_score: item.total_score,
                        population: item.population,
                        area_km2: item.area_km2,
                        rent_2ldk: item.rent_2ldk,
                        elementary_schools: item.elementary_schools,
                        waiting_children: item.waiting_children,
                      }}
                      isSelected={selectedAreas.some(a => a.id === item.area_id)}
                      onSelect={() => handleAreaClick({
                        id: item.area_id,
                        code: item.area_code,
                        name: item.area_name,
                        wellbeing_score: item.total_score,
                      })}
                      onViewDetail={() => handleViewDetail(item.area_id)}
                    />
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}