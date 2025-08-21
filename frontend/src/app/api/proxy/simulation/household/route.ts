import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'https://tokyo-wellbeing-map-api-mongo.onrender.com';

export const runtime = 'nodejs';

export async function POST(request: NextRequest): Promise<Response> {
  try {
    const body = await request.json();
    
    console.log('Simulation proxy request:', body);
    
    const response = await fetch(`${API_BASE_URL}/api/v1/simulation/household/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    const responseText = await response.text();
    console.log('Simulation API response status:', response.status);
    console.log('Simulation API response:', responseText);
    
    if (!response.ok) {
      return NextResponse.json(
        { 
          error: `Upstream returned ${response.status}`,
          details: responseText 
        },
        { status: response.status }
      );
    }
    
    // JSONとしてパースを試みる
    try {
      const data = JSON.parse(responseText);
      return NextResponse.json(data);
    } catch (parseError) {
      console.error('Failed to parse response as JSON:', parseError);
      return NextResponse.json(
        { error: 'Invalid response format from API' },
        { status: 500 }
      );
    }
    
  } catch (error: any) {
    console.error('Simulation proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to process simulation request', details: error.message },
      { status: 500 }
    );
  }
}