// API Client for fetching data from backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

interface FetchOptions {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: unknown;
  headers?: Record<string, string>;
}

async function fetchApi<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const { method = "GET", body, headers = {} } = options;

  const config: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Network error" }));
    throw new Error(error.message || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

// Peraturan API
export const peraturanApi = {
  // List all peraturan with pagination
  list: async (params?: {
    page?: number;
    limit?: number;
    kategori?: string;
    tahun?: number;
    search?: string;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set("page", params.page.toString());
    if (params?.limit) searchParams.set("limit", params.limit.toString());
    if (params?.kategori) searchParams.set("kategori", params.kategori);
    if (params?.tahun) searchParams.set("tahun", params.tahun.toString());
    if (params?.search) searchParams.set("q", params.search);

    const query = searchParams.toString();
    return fetchApi<{
      success: boolean;
      message: string;
      data: Array<{
        id: string;
        judul: string;
        nomor: string;
        tahun: number;
        kategori: string;
        tentang: string;
        status: string;
      }>;
      total: number;
      page: number;
      limit: number;
    }>(`/api/v1/peraturan${query ? `?${query}` : ""}`);
  },

  // Get peraturan by ID
  get: async (id: string) => {
    return fetchApi<{
      success: boolean;
      message: string;
      data: {
        id: string;
        judul: string;
        nomor: string;
        tahun: number;
        kategori: string;
        tentang: string;
        status: string;
        pdf_url: string;
        url: string;
        pemrakarsa: string;
        tempat_penetapan: string;
        tanggal_ditetapkan: string;
        tahun_diumulkan: number;
        metadata: Record<string, unknown>;
        created_at: string;
        updated_at: string;
      };
    }>(`/api/v1/peraturan/${id}`);
  },

  // Search peraturan
  search: async (query: string, params?: { page?: number; limit?: number }) => {
    const searchParams = new URLSearchParams();
    searchParams.set("q", query);
    if (params?.page) searchParams.set("page", params.page.toString());
    if (params?.limit) searchParams.set("limit", params.limit.toString());

    return fetchApi<{
      success: boolean;
      message: string;
      data: Array<{
        id: string;
        judul: string;
        nomor: string;
        tahun: number;
        kategori: string;
      }>;
      total: number;
      page: number;
      limit: number;
    }>(`/api/v1/peraturan/search?${searchParams.toString()}`);
  },

  // Get BAB list for peraturan
  getBabList: async (peraturanId: string) => {
    return fetchApi<{
      success: boolean;
      message: string;
      data: Array<{
        id: number;
        peraturan_id: string;
        nomor_bab: string;
        judul_bab: string;
        urutan: number;
      }>;
    }>(`/api/v1/peraturan/${peraturanId}/bab`);
  },

  // Get Pasal list for peraturan
  getPasalList: async (peraturanId: string) => {
    return fetchApi<{
      success: boolean;
      message: string;
      data: Array<{
        id: number;
        peraturan_id: string;
        bab_id: number | null;
        nomor_pasal: string;
        judul_pasal: string;
        konten_pasal: string;
        urutan: number;
      }>;
    }>(`/api/v1/peraturan/${peraturanId}/pasal`);
  },

  // Get Ayat list for pasal
  getAyatList: async (peraturanId: string, pasalId: number) => {
    return fetchApi<{
      success: boolean;
      message: string;
      data: Array<{
        id: number;
        pasal_id: number;
        nomor_ayat: string;
        konten_ayat: string;
        urutan: number;
      }>;
    }>(`/api/v1/peraturan/${peraturanId}/pasal/${pasalId}/ayat`);
  },
};

// Health check
export const healthApi = {
  check: async () => {
    return fetchApi<{ status: string }>(`/health`);
  },
};