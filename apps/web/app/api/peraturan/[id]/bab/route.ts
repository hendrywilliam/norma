import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL || "http://localhost:8080";

export async function GET(
	request: NextRequest,
	{ params }: { params: Promise<{ id: string }> },
) {
	try {
		const { id } = await params;

		const response = await fetch(`${API_URL}/api/v1/peraturan/${id}/bab`, {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
			},
			cache: "no-store",
		});

		if (!response.ok) {
			return NextResponse.json(
				{ success: false, message: "Failed to fetch bab list" },
				{ status: response.status },
			);
		}

		const data = await response.json();
		return NextResponse.json(data);
	} catch (error) {
		console.error("Get bab list error:", error);
		return NextResponse.json(
			{ success: false, message: "Failed to fetch bab list" },
			{ status: 500 },
		);
	}
}
