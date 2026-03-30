"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Search, ChevronLeft, ChevronRight, FileText, Loader2 } from "lucide-react";

const categoryColors: Record<string, string> = {
  UU: "bg-primary/10 text-primary hover:bg-primary/20",
  PP: "bg-civic-emerald/10 text-civic-emerald hover:bg-civic-emerald/20",
  Perpres: "bg-civic-amber/10 text-civic-amber hover:bg-civic-amber/20",
  Permen: "bg-civic-teal/10 text-civic-teal hover:bg-civic-teal/20",
  Perda: "bg-pink-100 text-pink-800 hover:bg-pink-200",
};

const categories = ["Semua", "UU", "PP", "Perpres", "Permen", "Perda"];

interface Peraturan {
  id: string;
  judul: string;
  nomor: string;
  tahun: number;
  kategori: string;
  tentang: string;
  status: string;
}

interface PeraturanResponse {
  success: boolean;
  message: string;
  data: Peraturan[];
  total: number;
  page: number;
  limit: number;
}

export default function PeraturanListContent() {
  const searchParams = useSearchParams();
  const categoryParam = searchParams.get("kategori");
  
  const [selectedCategory, setSelectedCategory] = useState(categoryParam || "Semua");
  const [searchQuery, setSearchQuery] = useState("");
  const [peraturan, setPeraturan] = useState<Peraturan[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchPeraturan() {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        params.set("page", page.toString());
        params.set("limit", "20");
        if (selectedCategory !== "Semua") {
          params.set("kategori", selectedCategory);
        }
        if (searchQuery) {
          params.set("search", searchQuery);
        }

        const res = await fetch(`/api/peraturan?${params.toString()}`);
        if (!res.ok) {
          throw new Error("Failed to fetch peraturan");
        }
        const data: PeraturanResponse = await res.json();
        setPeraturan(data.data || []);
        setTotal(data.total || 0);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
        setPeraturan([]);
      } finally {
        setLoading(false);
      }
    }

    fetchPeraturan();
  }, [selectedCategory, searchQuery, page]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Daftar Peraturan</h1>
          <p className="text-muted-foreground">Temukan peraturan perundang-undangan Indonesia</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <FileText className="h-4 w-4" />
          <span>{loading ? "Memuat..." : `${total} peraturan ditemukan`}</span>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Cari judul, nomor, atau kata kunci..."
            className="pl-9"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setPage(1);
            }}
          />
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {categories.map((category) => (
            <Button
              key={category}
              variant={selectedCategory === category ? "default" : "outline"}
              size="sm"
              onClick={() => {
                setSelectedCategory(category);
                setPage(1);
              }}
            >
              {category}
            </Button>
          ))}
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
          <p className="font-medium">Error</p>
          <p className="text-sm">{error}</p>
          <p className="text-sm mt-2">
            Pastikan backend API berjalan di {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"}
          </p>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && peraturan.length === 0 && (
        <div className="rounded-lg border border-border bg-card p-8 text-center">
          <p className="text-muted-foreground">Tidak ada peraturan ditemukan</p>
          <p className="text-sm text-muted-foreground mt-2">
            Coba ubah filter atau kata kunci pencarian
          </p>
        </div>
      )}

      {/* Results */}
      {!loading && !error && peraturan.length > 0 && (
        <div className="rounded-lg border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[100px]">Kategori</TableHead>
                <TableHead>Judul</TableHead>
                <TableHead className="w-[80px]">Nomor</TableHead>
                <TableHead className="w-[80px]">Tahun</TableHead>
                <TableHead className="w-[100px]">Status</TableHead>
                <TableHead className="w-[80px]">Aksi</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {peraturan.map((p) => (
                <TableRow key={p.id} className="hover:bg-muted/50">
                  <TableCell>
                    <Badge className={categoryColors[p.kategori] || "bg-muted text-muted-foreground"}>
                      {p.kategori}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Link
                      href={`/peraturan/${p.id}`}
                      className="font-medium text-foreground hover:text-primary line-clamp-1"
                    >
                      {p.judul}
                    </Link>
                    <p className="text-sm text-muted-foreground line-clamp-1">{p.tentang}</p>
                  </TableCell>
                  <TableCell className="font-medium">{p.nomor}</TableCell>
                  <TableCell>{p.tahun}</TableCell>
                  <TableCell>
                    <span className="inline-flex items-center rounded-full bg-civic-emerald/10 px-2 py-1 text-xs font-medium text-civic-emerald">
                      {p.status}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm" asChild>
                      <Link href={`/peraturan/${p.id}`}>Detail</Link>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Pagination */}
      {!loading && !error && total > 20 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Halaman {page} dari {Math.ceil(total / 20)}
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
            >
              <ChevronLeft className="h-4 w-4" />
              Sebelumnya
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page * 20 >= total}
              onClick={() => setPage(page + 1)}
            >
              Selanjutnya
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}