// Simple API route for voice query proxy
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  // In a real implementation, we would forward to the backend
  // For now, we'll return a mock response
  return NextResponse.json({
    transcript: "This is a mock transcript",
    answer: "This is a mock answer from the RAG pipeline.",
    latency_ms: 150
  });
}

export async function GET(request: NextRequest) {
  return NextResponse.json({ status: 'ok' });
}