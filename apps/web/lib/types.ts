// Peraturan Types

export interface Peraturan {
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
}

export interface PeraturanListResponse {
  data: Peraturan[];
  total: number;
  page: number;
  limit: number;
}

export interface Bab {
  id: number;
  peraturan_id: string;
  nomor_bab: string;
  judul_bab: string;
  urutan: number;
  created_at: string;
  updated_at: string;
}

export interface Pasal {
  id: number;
  peraturan_id: string;
  bab_id: number | null;
  nomor_pasal: string;
  judul_pasal: string;
  konten_pasal: string;
  urutan: number;
  created_at: string;
  updated_at: string;
}

export interface Ayat {
  id: number;
  pasal_id: number;
  nomor_ayat: string;
  konten_ayat: string;
  urutan: number;
  created_at: string;
  updated_at: string;
}

export interface PeraturanDetail extends Peraturan {
  bab_list: Bab[];
  pasal_list: Pasal[];
  ayat_list: Ayat[];
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface ApiListResponse<T> {
  success: boolean;
  message: string;
  data: T[];
  total: number;
  page: number;
  limit: number;
}