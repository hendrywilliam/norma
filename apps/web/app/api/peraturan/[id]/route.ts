import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    const response = await fetch(`${API_BASE_URL}/api/v1/peraturan/${id}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { success: false, message: "Peraturan not found" },
          { status: 404 }
        );
      }
      const error = await response.json().catch(() => ({ message: "Failed to fetch peraturan" }));
      return NextResponse.json(
        { success: false, message: error.message },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Get peraturan error:", error);
    return NextResponse.json(
      { success: false, message: "Failed to fetch peraturan" },
      { status: 500 }
    );
  }
}