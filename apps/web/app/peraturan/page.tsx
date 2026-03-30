"use client";

import { useState } from "react";
import Link from "next/link";
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
import { Search, ChevronLeft, ChevronRight, FileText } from "lucide-react";

const categoryColors: Record<string, string> = {
  UU: "bg-primary/10 text-primary hover:bg-primary/20",
  PP: "bg-civic-emerald/10 text-civic-emerald hover:bg-civic-emerald/20",
  Perpres: "bg-civic-amber/10 text-civic-amber hover:bg-civic-amber/20",
  Permen: "bg-civic-teal/10 text-civic-teal hover:bg-civic-teal/20",
  Perda: "bg-pink-100 text-pink-800 hover:bg-pink-200",
};

const categories = ["Semua", "UU", "PP", "Perpres", "Permen", "Perda"];

const mockPeraturan = [
  {
    id: "UU_13_2024_abc123",
    title: "Undang-Undang tentang Cipta Kerja",
    nomor: "11",
    tahun: 2024,
    kategori: "UU",
    status: "Berlaku",
    tentang: "Undang-Undang tentang Cipta Kerja",
  },
  {
    id: "PP_35_2024_def456",
    title: "Peraturan Pemerintah tentang Penyelenggaraan Perumahan",
    nomor: "35",
    tahun: 2024,
    kategori: "PP",
    status: "Berlaku",
    tentang: "Peraturan Pemerintah tentang Penyelenggaraan Perumahan",
  },
  {
    id: "Perpres_12_2024_ghi789",
    title: "Peraturan Presiden tentang Rencana Pembangunan Jangka Menengah",
    nomor: "12",
    tahun: 2024,
    kategori: "Perpres",
    status: "Berlaku",
    tentang: "Peraturan Presiden tentang Rencana Pembangunan Jangka Menengah Nasional",
  },
  {
    id: "UU_5_2024_jkl012",
    title: "Undang-Undang tentang Perubahan atas Undang-Undang tentang Otonomi Khusus",
    nomor: "5",
    tahun: 2024,
    kategori: "UU",
    status: "Berlaku",
    tentang: "Perubahan atas UU Otonomi Khusus Provinsi Papua",
  },
  {
    id: "Permen_23_2024_mno345",
    title: "Peraturan Menteri tentang Standar Pelayanan Publik",
    nomor: "23",
    tahun: 2024,
    kategori: "Permen",
    status: "Berlaku",
    tentang: "Peraturan Menteri PANRB tentang Standar Pelayanan Publik",
  },
];

export default function PeraturanListPage() {
  const [selectedCategory, setSelectedCategory] = useState("Semua");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredPeraturan = mockPeraturan.filter((p) => {
    const matchesCategory = selectedCategory === "Semua" || p.kategori === selectedCategory;
    const matchesSearch =
      searchQuery === "" ||
      p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.nomor.includes(searchQuery);
    return matchesCategory && matchesSearch;
  });

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
          <span>{filteredPeraturan.length} peraturan ditemukan</span>
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
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {categories.map((category) => (
            <Button
              key={category}
              variant={selectedCategory === category ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory(category)}
            >
              {category}
            </Button>
          ))}
        </div>
      </div>

      {/* Results */}
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
            {filteredPeraturan.map((peraturan) => (
              <TableRow key={peraturan.id} className="hover:bg-muted/50">
                <TableCell>
                  <Badge className={categoryColors[peraturan.kategori] || "bg-muted text-muted-foreground"}>
                    {peraturan.kategori}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Link
                    href={`/peraturan/${peraturan.id}`}
                    className="font-medium text-foreground hover:text-primary line-clamp-1"
                  >
                    {peraturan.title}
                  </Link>
                  <p className="text-sm text-muted-foreground line-clamp-1">{peraturan.tentang}</p>
                </TableCell>
                <TableCell className="font-medium">{peraturan.nomor}</TableCell>
                <TableCell>{peraturan.tahun}</TableCell>
                <TableCell>
                  <span className="inline-flex items-center rounded-full bg-civic-emerald/10 px-2 py-1 text-xs font-medium text-civic-emerald">
                    {peraturan.status}
                  </span>
                </TableCell>
                <TableCell>
                  <Button variant="ghost" size="sm" asChild>
                    <Link href={`/peraturan/${peraturan.id}`}>Detail</Link>
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Menampilkan 1-{filteredPeraturan.length} dari {filteredPeraturan.length} peraturan
        </p>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled>
            <ChevronLeft className="h-4 w-4" />
            Sebelumnya
          </Button>
          <Button variant="outline" size="sm" disabled>
            Selanjutnya
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}