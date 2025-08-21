import React from 'react';

interface LoadingSkeletonProps {
  variant?: 'card' | 'text' | 'button' | 'image';
  className?: string;
  count?: number;
}

export function LoadingSkeleton({ 
  variant = 'text', 
  className = '', 
  count = 1 
}: LoadingSkeletonProps) {
  const getSkeletonClass = () => {
    const baseClass = 'animate-pulse bg-gray-200 rounded';
    
    switch (variant) {
      case 'card':
        return `${baseClass} h-64 w-full`;
      case 'text':
        return `${baseClass} h-4 w-full`;
      case 'button':
        return `${baseClass} h-10 w-24`;
      case 'image':
        return `${baseClass} h-48 w-full`;
      default:
        return baseClass;
    }
  };

  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className={`${getSkeletonClass()} ${className} ${
            count > 1 && index < count - 1 ? 'mb-2' : ''
          }`}
        />
      ))}
    </>
  );
}

// エリアカード用のスケルトン
export function AreaCardSkeleton() {
  return (
    <div className="border rounded-lg p-4 shadow-sm">
      <LoadingSkeleton variant="text" className="h-6 w-3/4 mb-4" />
      <LoadingSkeleton variant="text" className="h-4 w-1/2 mb-2" />
      <LoadingSkeleton variant="text" className="h-4 w-2/3 mb-4" />
      <div className="flex justify-between items-center">
        <LoadingSkeleton variant="text" className="h-8 w-20" />
        <LoadingSkeleton variant="button" />
      </div>
    </div>
  );
}

// エリアリスト用のスケルトン
export function AreaListSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, index) => (
        <AreaCardSkeleton key={index} />
      ))}
    </div>
  );
}