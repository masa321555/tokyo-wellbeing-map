'use client';

import React, { useState, useMemo } from 'react';

interface TownListWithFilterProps {
  townListWithStations: string[];
  wardName: string;
}

export function TownListWithFilter({ townListWithStations, wardName }: TownListWithFilterProps) {
  const [selectedLine, setSelectedLine] = useState<string | null>(null);

  // 路線情報を抽出してユニークなリストを作成
  const railwayLines = useMemo(() => {
    const linesSet = new Set<string>();
    
    townListWithStations.forEach(townWithStation => {
      const match = townWithStation.match(/^(.+?)（(.+?)）$/);
      if (match && match[2]) {
        const stationInfo = match[2];
        // 駅名｜路線 の形式から路線部分を抽出
        const lineMatch = stationInfo.match(/.*?｜(.+)$/);
        if (lineMatch && lineMatch[1]) {
          // 複数路線の場合は分割
          const lines = lineMatch[1].split('、');
          lines.forEach(line => {
            linesSet.add(line.trim());
          });
        }
      }
    });
    
    return Array.from(linesSet).sort();
  }, [townListWithStations]);

  // フィルタリングされた町リスト
  const filteredTowns = useMemo(() => {
    if (!selectedLine) return townListWithStations;
    
    return townListWithStations.filter(townWithStation => {
      const match = townWithStation.match(/^(.+?)（(.+?)）$/);
      if (match && match[2]) {
        const stationInfo = match[2];
        const lineMatch = stationInfo.match(/.*?｜(.+)$/);
        if (lineMatch && lineMatch[1]) {
          return lineMatch[1].includes(selectedLine);
        }
      }
      return false;
    });
  }, [townListWithStations, selectedLine]);

  return (
    <>
      {/* 路線フィルターボタン */}
      {railwayLines.length > 0 && (
        <div className="mb-6 border-b border-gray-200 pb-4">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedLine(null)}
              className={`px-3 py-1.5 text-sm rounded-full transition-colors ${
                selectedLine === null
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              すべて
            </button>
            {railwayLines.map(line => (
              <button
                key={line}
                onClick={() => setSelectedLine(line)}
                className={`px-3 py-1.5 text-sm rounded-full transition-colors ${
                  selectedLine === line
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {line}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 町名リスト */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
        {filteredTowns.map((townWithStation, index) => {
          // 町名と駅情報を分離
          const match = townWithStation.match(/^(.+?)（(.+?)）$/);
          const townName = match ? match[1] : townWithStation;
          const stationInfo = match ? match[2] : null;
          
          return (
            <div key={index} className="bg-gray-50 rounded-md p-3 hover:bg-gray-100 transition-colors">
              <div className="font-medium text-gray-800">{townName}</div>
              {stationInfo && (
                <div className="mt-1 text-sm text-gray-600">
                  🚃 {stationInfo}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <p className="text-sm text-gray-600 mt-4">
        {selectedLine && (
          <span className="font-medium text-blue-600">{selectedLine} </span>
        )}
        {filteredTowns.length} / {townListWithStations.length} 町
      </p>
    </>
  );
}