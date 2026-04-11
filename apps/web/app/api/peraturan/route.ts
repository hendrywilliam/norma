import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL || "http://localhost:8080";

export async function GET(request: NextRequest) {
	try {
		const searchParams = request.nextUrl.searchParams;
		const page = searchParams.get("page") || "1";
		const limit = searchParams.get("limit") || "20";
		const kategori = searchParams.get("kategori");
		const tahun = searchParams.get("tahun");
		const search = searchParams.get("search");

		const params = new URLSearchParams();
		params.set("page", page);
		params.set("limit", limit);
		if (kategori) params.set("kategori", kategori);
		if (tahun) params.set("tahun", tahun);
		if (search) params.set("search", search);

		const response = await fetch(
			`${API_URL}/api/v1/peraturan?${params.toString()}`,
			{
				method: "GET",
				headers: {
					"Content-Type": "application/json",
				},
				cache: "no-store",
			},
		);

		if (!response.ok) {
			const error = await response
				.json()
				.catch(() => ({ message: "Failed to fetch peraturan" }));
			return NextResponse.json(
				{ success: false, message: error.message },
				{ status: response.status },
			);
		}

		const data = await response.json();
		return NextResponse.json(data);
	} catch (error) {
		console.error("Get peraturan list error:", error);
		return NextResponse.json(
			{ success: false, message: "Failed to fetch peraturan list" },
			{ status: 500 },
		);
	}
}
