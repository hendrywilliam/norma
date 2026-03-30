"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { 
  ChevronLeft, 
  Download, 
  Share2, 
  Calendar, 
  Building, 
  FileText,
  BookOpen,
  ExternalLink,
  ChevronRight
} from "lucide-react";
import { useState } from "react";

const categoryColors: Record<string, string> = {
  UU: "bg-primary/10 text-primary",
  PP: "bg-civic-emerald/10 text-civic-emerald",
  Perpres: "bg-civic-amber/10 text-civic-amber",
  Permen: "bg-civic-teal/10 text-civic-teal",
};

const mockPeraturan = {
  id: "UU_11_2024_abc123",
  judul: "Undang-Undang tentang Informasi dan Transaksi Elektronik",
  nomor: "11",
  tahun: 2024,
  kategori: "UU",
  jenisPeraturan: "Undang-Undang",
  status: "Berlaku",
  tentang: "Undang-Undang tentang Informasi dan Transaksi Elektronik",
  pemrakarsa: "Kementerian Komunikasi dan Informatika",
  tempatPenetapan: "Jakarta",
  tanggalDitetapkan: "2024-01-15",
  tahunDiumulkan: "2024",
  pdfUrl: "https://peraturan.go.id/download/uu_11_2024.pdf",
  url: "https://peraturan.go.id/id/uu_11_2024",
};

const mockBab = [
  { id: 1, nomorBab: "I", judulBab: "Ketentuan Umum", jumlahPasal: 5 },
  { id: 2, nomorBab: "II", judulBab: "Asas dan Tujuan", jumlahPasal: 3 },
  { id: 3, nomorBab: "III", judulBab: "Informasi dan Dokumen Elektronik", jumlahPasal: 12 },
  { id: 4, nomorBab: "IV", judulBab: "Transaksi Elektronik", jumlahPasal: 8 },
  { id: 5, nomorBab: "V", judulBab: "Tanda Tangan Elektronik", jumlahPasal: 6 },
  { id: 6, nomorBab: "VI", judulBab: "Penyelenggaraan Sistem Elektronik", jumlahPasal: 15 },
  { id: 7, nomorBab: "VII", judulBab: "Sertifikasi Elektronik", jumlahPasal: 4 },
  { id: 8, nomorBab: "VIII", judulBab: "Ketentuan Pidana", jumlahPasal: 10 },
  { id: 9, nomorBab: "IX", judulBab: "Ketentuan Peralihan", jumlahPasal: 2 },
  { id: 10, nomorBab: "X", judulBab: "Ketentuan Penutup", jumlahPasal: 3 },
];

const mockPasal = [
  { nomor: "1", konten: "Dalam Undang-Undang ini yang dimaksud dengan...", ayatCount: 5 },
  { nomor: "2", konten: "Informasi Elektronik adalah satu informasi atau...", ayatCount: 3 },
  { nomor: "3", konten: "Transaksi Elektronik adalah perbuatan hukum...", ayatCount: 4 },
];

export default function PeraturanDetailPage() {
  const [expandedBab, setExpandedBab] = useState<number | null>(null);

  return (
    <div className="space-y-8">
      {/* Back Button */}
      <div>
        <Button variant="ghost" size="sm" asChild>
          <Link href="/peraturan" className="flex items-center gap-2">
            <ChevronLeft className="h-4 w-4" />
            Kembali ke Daftar Peraturan
          </Link>
        </Button>
      </div>

      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Badge className={categoryColors[mockPeraturan.kategori] || "bg-muted text-muted-foreground"}>
                  {mockPeraturan.kategori}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  {mockPeraturan.jenisPeraturan} Nomor {mockPeraturan.nomor} Tahun {mockPeraturan.tahun}
                </span>
              </div>
              <CardTitle className="text-2xl">{mockPeraturan.judul}</CardTitle>
              <p className="text-muted-foreground">{mockPeraturan.tentang}</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <Share2 className="h-4 w-4 mr-2" />
                Bagikan
              </Button>
              <Button size="sm" asChild>
                <a href={mockPeraturan.pdfUrl} target="_blank" rel="noopener noreferrer">
                  <Download className="h-4 w-4 mr-2" />
                  Download PDF
                </a>
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div className="flex items-center gap-2">
              <Building className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Pemrakarsa:</span>
              <span className="text-sm font-medium">{mockPeraturan.pemrakarsa}</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Ditetapkan:</span>
              <span className="text-sm font-medium">{mockPeraturan.tanggalDitetapkan}</span>
            </div>
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Status:</span>
              <span className="inline-flex items-center rounded-full bg-civic-emerald/10 px-2 py-0.5 text-xs font-medium text-civic-emerald">
                {mockPeraturan.status}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <ExternalLink className="h-4 w-4 text-muted-foreground" />
              <a
                href={mockPeraturan.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-medium text-primary hover:underline"
              >
                Lihat di Peraturan.go.id
              </a>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Content Tabs */}
      <div className="flex border-b">
        <button className="px-4 py-2 text-sm font-medium text-primary border-b-2 border-primary">
          Struktur
        </button>
        <button className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground">
          Info Lengkap
        </button>
        <button className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground">
          Riwayat
        </button>
      </div>

      {/* BAB List */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            Daftar BAB
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y">
            {mockBab.map((bab) => (
              <div key={bab.id}>
                <button
                  className="w-full flex items-center justify-between p-4 hover:bg-muted/50 transition-colors text-left"
                  onClick={() => setExpandedBab(expandedBab === bab.id ? null : bab.id)}
                >
                  <div className="flex items-center gap-3">
                    <ChevronRight
                      className={`h-4 w-4 text-muted-foreground transition-transform ${
                        expandedBab === bab.id ? "rotate-90" : ""
                      }`}
                    />
                    <span className="font-medium">BAB {bab.nomorBab}</span>
                    <span className="text-muted-foreground">{bab.judulBab}</span>
                  </div>
                  <Badge variant="secondary">{bab.jumlahPasal} Pasal</Badge>
                </button>
                
                {expandedBab === bab.id && (
                  <div className="bg-muted/30 p-4 pl-12">
                    <p className="text-sm text-muted-foreground mb-4">
                      BAB {bab.nomorBab} berisi {bab.jumlahPasal} pasal yang membahas tentang {bab.judulBab.toLowerCase()}.
                    </p>
                    <Button variant="outline" size="sm">
                      Lihat Semua Pasal
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Preview Pasal */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Preview Pasal</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[80px]">Pasal</TableHead>
                <TableHead>Isi Ringkas</TableHead>
                <TableHead className="w-[80px]">Ayat</TableHead>
                <TableHead className="w-[80px]">Aksi</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockPasal.map((pasal) => (
                <TableRow key={pasal.nomor} className="hover:bg-muted/50">
                  <TableCell className="font-medium">Pasal {pasal.nomor}</TableCell>
                  <TableCell className="text-muted-foreground line-clamp-2">{pasal.konten}</TableCell>
                  <TableCell>{pasal.ayatCount} ayat</TableCell>
                  <TableCell>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      asChild
                    >
                      <Link href={`/peraturan/${mockPeraturan.id}/pasal/${pasal.nomor}`}>
                        Detail
                      </Link>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}