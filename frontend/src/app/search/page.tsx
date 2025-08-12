'use client';

import React from 'react';

export default function SearchPage() {
  // 検索ページはホームページと統合されているため、リダイレクト
  if (typeof window !== 'undefined') {
    window.location.href = '/';
  }
  
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="text-center text-gray-500">ホームページにリダイレクトしています...</div>
    </div>
  );
}