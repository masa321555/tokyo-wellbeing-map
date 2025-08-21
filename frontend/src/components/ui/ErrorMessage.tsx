import React from 'react';
// import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface ErrorMessageProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  requestId?: string;
}

export function ErrorMessage({ 
  title = 'エラーが発生しました',
  message = 'データの取得中にエラーが発生しました。しばらくしてからもう一度お試しください。',
  onRetry,
  requestId
}: ErrorMessageProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6">
      <div className="flex items-start">
        {/* <ExclamationTriangleIcon className="h-6 w-6 text-red-600 mt-0.5" /> */}
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-red-800">{title}</h3>
          <p className="mt-1 text-sm text-red-700">{message}</p>
          {requestId && (
            <p className="mt-2 text-xs text-red-600">
              リクエストID: {requestId}
            </p>
          )}
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 text-sm font-medium text-red-600 hover:text-red-500"
            >
              もう一度試す →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ネットワークエラー用
export function NetworkErrorMessage({ onRetry }: { onRetry?: () => void }) {
  return (
    <ErrorMessage
      title="接続エラー"
      message="サーバーへの接続に失敗しました。インターネット接続を確認してください。"
      onRetry={onRetry}
    />
  );
}

// タイムアウトエラー用
export function TimeoutErrorMessage({ onRetry }: { onRetry?: () => void }) {
  return (
    <ErrorMessage
      title="タイムアウトエラー"
      message="サーバーからの応答がありません。時間をおいてからもう一度お試しください。"
      onRetry={onRetry}
    />
  );
}

// 503エラー用
export function ServiceUnavailableMessage({ onRetry }: { onRetry?: () => void }) {
  return (
    <ErrorMessage
      title="サービス一時停止中"
      message="現在サービスはメンテナンス中です。しばらくしてからアクセスしてください。"
      onRetry={onRetry}
    />
  );
}