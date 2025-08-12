'use client';

import React, { useState } from 'react';
import * as Slider from '@radix-ui/react-slider';
import { useStore } from '@/store/useStore';

export const SearchFilters: React.FC = () => {
  const { searchParams, setSearchParams } = useStore();
  const [localParams, setLocalParams] = useState(searchParams);

  const handleRentChange = (field: 'maxRent' | 'minRent', value: number) => {
    setLocalParams({ ...localParams, [field]: value });
  };

  const handleApplyFilters = () => {
    setSearchParams(localParams);
  };

  const handleReset = () => {
    setLocalParams({});
    setSearchParams({});
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">検索条件</h3>

      {/* 家賃範囲 */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700">
          家賃（2LDK）: {localParams.minRent || 0}万円 〜 {localParams.maxRent || 50}万円
        </label>
        <div className="px-2">
          <Slider.Root
            className="relative flex items-center select-none touch-none w-full h-5"
            value={[
              isNaN(localParams.minRent as number) ? 0 : (localParams.minRent || 0),
              isNaN(localParams.maxRent as number) ? 50 : (localParams.maxRent || 50)
            ]}
            onValueChange={([min, max]) => {
              handleRentChange('minRent', min);
              handleRentChange('maxRent', max);
            }}
            max={50}
            min={0}
            step={1}
          >
            <Slider.Track className="bg-gray-200 relative grow rounded-full h-2">
              <Slider.Range className="absolute bg-blue-500 rounded-full h-full" />
            </Slider.Track>
            <Slider.Thumb
              className="block w-5 h-5 bg-white shadow-md rounded-full hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="最小家賃"
            />
            <Slider.Thumb
              className="block w-5 h-5 bg-white shadow-md rounded-full hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="最大家賃"
            />
          </Slider.Root>
        </div>
      </div>

      {/* 間取り */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">間取り</label>
        <select
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={localParams.roomType || ''}
          onChange={(e) => setLocalParams({ ...localParams, roomType: e.target.value })}
        >
          <option value="">すべて</option>
          <option value="1R">1R</option>
          <option value="1K">1K</option>
          <option value="1DK">1DK</option>
          <option value="1LDK">1LDK</option>
          <option value="2LDK">2LDK</option>
          <option value="3LDK">3LDK</option>
        </select>
      </div>

      {/* 教育環境 */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">小中学校数（最小）</label>
        <input
          type="number"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={localParams.minSchools || ''}
          onChange={(e) => {
            const value = parseInt(e.target.value);
            setLocalParams({
              ...localParams,
              minSchools: isNaN(value) ? undefined : value,
            });
          }}
          placeholder="例: 5"
          min="0"
        />
      </div>

      {/* 待機児童 */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">待機児童数（最大）</label>
        <input
          type="number"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={localParams.maxWaitingChildren ?? ''}
          onChange={(e) => {
            const value = parseInt(e.target.value);
            setLocalParams({
              ...localParams,
              maxWaitingChildren: isNaN(value) ? undefined : value,
            });
          }}
          placeholder="例: 0"
          min="0"
        />
      </div>

      {/* 公園 */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">公園数（最小）</label>
        <input
          type="number"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={localParams.minParks || ''}
          onChange={(e) => {
            const value = parseInt(e.target.value);
            setLocalParams({
              ...localParams,
              minParks: isNaN(value) ? undefined : value,
            });
          }}
          placeholder="例: 10"
          min="0"
        />
      </div>

      {/* レジャー施設 */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">映画館数（最小）</label>
        <input
          type="number"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={localParams.minMovieTheaters || ''}
          onChange={(e) => {
            const value = parseInt(e.target.value);
            setLocalParams({
              ...localParams,
              minMovieTheaters: isNaN(value) ? undefined : value,
            });
          }}
          placeholder="例: 1"
          min="0"
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">テーマパーク・遊園地</label>
        <select
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={localParams.hasThemeParks || ''}
          onChange={(e) => setLocalParams({ ...localParams, hasThemeParks: e.target.value })}
        >
          <option value="">指定なし</option>
          <option value="yes">あり</option>
          <option value="no">なし</option>
        </select>
      </div>

      {/* ボタン */}
      <div className="flex gap-2 pt-4">
        <button
          onClick={handleApplyFilters}
          className="flex-1 px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
        >
          検索
        </button>
        <button
          onClick={handleReset}
          className="px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded-md hover:bg-gray-300 transition-colors"
        >
          リセット
        </button>
      </div>
    </div>
  );
};