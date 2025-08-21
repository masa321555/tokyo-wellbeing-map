import { NextRequest, NextResponse } from 'next/server';
import { PROXY_CONFIG, fetchWithRetry, logError, logAccess, getCacheHeaders } from '@/lib/proxy-config';

// ランタイム指定（Node.jsランタイムを使用）
export const runtime = 'nodejs';

export async function GET(request: NextRequest): Promise<Response> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  
  try {
    // クエリパラメータを取得
    const searchParams = request.nextUrl.searchParams;
    const skip = searchParams.get('skip') || '0';
    const limit = searchParams.get('limit') || '100';
    
    // パラメータ検証
    const skipNum = parseInt(skip);
    const limitNum = parseInt(limit);
    
    if (isNaN(skipNum) || skipNum < 0) {
      return NextResponse.json(
        { error: 'Invalid skip parameter', requestId },
        { status: 400 }
      );
    }
    
    if (isNaN(limitNum) || limitNum < 1 || limitNum > 100) {
      return NextResponse.json(
        { error: 'Invalid limit parameter (1-100)', requestId },
        { status: 400 }
      );
    }
    
    // タイムアウト付きfetch with retry
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), PROXY_CONFIG.TIMEOUT);
    
    const upstreamUrl = `${PROXY_CONFIG.API_BASE_URL}/api/v1/areas/?skip=${skipNum}&limit=${limitNum}`;
    
    const response = await fetchWithRetry(
      upstreamUrl,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': requestId,
        },
        signal: controller.signal,
      }
    );
    
    clearTimeout(timeoutId);
    
    const latency = Date.now() - startTime;
    
    // アクセスログ出力
    logAccess({
      requestId,
      endpoint: '/api/proxy/areas',
      upstream: upstreamUrl,
      status: response.status,
      latency,
      timestamp: new Date().toISOString(),
      params: { skip: skipNum, limit: limitNum },
    });
    
    // エラーレスポンスの場合
    if (!response.ok) {
      return NextResponse.json(
        { error: `Upstream returned ${response.status}`, requestId },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    
    // レスポンスヘッダー
    const headers: HeadersInit = {
      'X-Request-ID': requestId,
      'X-Response-Time': latency.toString(),
      ...getCacheHeaders('areas'),
    };
    
    return NextResponse.json(data, { headers });
    
  } catch (error: any) {
    const latency = Date.now() - startTime;
    
    // エラーログ出力
    logError({
      requestId,
      endpoint: '/api/proxy/areas',
      error: error.message,
      type: error.name === 'AbortError' ? 'timeout' : 'network',
      latency,
      timestamp: new Date().toISOString(),
      details: {
        name: error.name,
        stack: error.stack,
      },
    });
    
    if (error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Request timeout', requestId },
        { status: 504 }
      );
    }
    
    return NextResponse.json(
      { error: 'Network error', requestId },
      { status: 503 }
    );
  }
}