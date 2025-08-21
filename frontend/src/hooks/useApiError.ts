import { useState, useCallback } from 'react';
import { AxiosError } from 'axios';

export interface ApiError {
  message: string;
  status?: number;
  requestId?: string;
  type: 'network' | 'timeout' | 'server' | 'unknown';
}

export function useApiError() {
  const [error, setError] = useState<ApiError | null>(null);
  const [isRetrying, setIsRetrying] = useState(false);

  const handleError = useCallback((err: unknown): ApiError => {
    let apiError: ApiError;

    if (err instanceof AxiosError) {
      if (err.code === 'ECONNABORTED' || err.message.includes('timeout')) {
        apiError = {
          message: 'リクエストがタイムアウトしました',
          type: 'timeout',
          status: 504,
        };
      } else if (!err.response) {
        apiError = {
          message: 'ネットワークエラーが発生しました',
          type: 'network',
        };
      } else {
        const status = err.response.status;
        const data = err.response.data;
        
        apiError = {
          message: data?.error || getErrorMessageByStatus(status),
          status,
          requestId: data?.requestId,
          type: 'server',
        };
      }
    } else if (err instanceof Error) {
      apiError = {
        message: err.message,
        type: 'unknown',
      };
    } else {
      apiError = {
        message: '予期しないエラーが発生しました',
        type: 'unknown',
      };
    }

    setError(apiError);
    return apiError;
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const retry = useCallback(async (retryFn: () => Promise<any>) => {
    setIsRetrying(true);
    clearError();
    
    try {
      const result = await retryFn();
      return result;
    } catch (err) {
      handleError(err);
      throw err;
    } finally {
      setIsRetrying(false);
    }
  }, [clearError, handleError]);

  return {
    error,
    isRetrying,
    handleError,
    clearError,
    retry,
  };
}

function getErrorMessageByStatus(status: number): string {
  switch (status) {
    case 400:
      return '不正なリクエストです';
    case 401:
      return '認証エラーです';
    case 403:
      return 'アクセスが拒否されました';
    case 404:
      return 'データが見つかりません';
    case 500:
      return 'サーバーエラーが発生しました';
    case 502:
      return 'ゲートウェイエラーが発生しました';
    case 503:
      return 'サービスが一時的に利用できません';
    case 504:
      return 'ゲートウェイタイムアウトが発生しました';
    default:
      return `エラーが発生しました (${status})`;
  }
}