import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'https://tokyo-wellbeing-map-api-mongo.onrender.com';

export const runtime = 'nodejs';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ areaId: string }> }
): Promise<Response> {
  try {
    const { areaId } = await params;
    
    const response = await fetch(`${API_BASE_URL}/api/v1/congestion-google/area/${areaId}/live`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { error: `Upstream returned ${response.status}` },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    
    return NextResponse.json(data, {
      headers: {
        'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=300',
      },
    });
    
  } catch (error: any) {
    console.error('Live congestion proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch live congestion data' },
      { status: 500 }
    );
  }
}