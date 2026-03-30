"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
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
  ChevronRight,
  Loader2
} from "lucide-react";
import { useState, useEffect } from "react";

const categoryColors: Record<string, string> = {
  UU: "bg-primary/10 text-primary",
  PP: "bg-civic-emerald/10 text-civic-emerald",
  Perpres: "bg-civic-amber/10 text-civic-amber",
  Permen: "bg-civic-teal/10 text-civic-teal",
};

interface Peraturan {
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
  tanggal_ditetapkan: string;
}

interface Bab {
  id: number;
  nomor_bab: string;
  judul_bab: string;
  urutan: number;
}

interface Pasal {
  id: number;
  nomor_pasal: string;
  judul_pasal: string;
  konten_pasal: string;
  urutan: number;
}

export default function PeraturanDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [peraturan, setPeraturan] = useState<Peraturan | null>(null);
  const [babList, setBabList] = useState<Bab[]>([]);
  const [pasalList, setPasalList] = useState<Pasal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedBab, setExpandedBab] = useState<number | null>(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        // Fetch peraturan detail
        const peraturanRes = await fetch(`/api/peraturan/${id}`);
        if (!peraturanRes.ok) {
          throw new Error("Failed to fetch peraturan");
        }
        const peraturanData = await peraturanRes.json();
        setPeraturan(peraturanData.data);

        // Fetch bab list
        const babRes = await fetch(`/api/peraturan/${id}/bab`);
        if (babRes.ok) {
          const babData = await babRes.json();
          setBabList(babData.data || []);
        }

        // Fetch pasal list
        const pasalRes = await fetch(`/api/peraturan/${id}/pasal`);
        if (pasalRes.ok) {
          const pasalData = await pasalRes.json();
          setPasalList(pasalData.data || []);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    }

    if (id) {
      fetchData();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !peraturan) {
    return (
      <div className="space-y-8">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/peraturan" className="flex items-center gap-2">
            <ChevronLeft className="h-4 w-4" />
            Kembali ke Daftar Peraturan
          </Link>
        </Button>
        <Card>
          <CardContent className="p-8 text-center">
            <p className="text-muted-foreground">{error || "Peraturan tidak ditemukan"}</p>
            <p className="text-sm text-muted-foreground mt-2">
              Pastikan backend API berjalan dan data tersedia.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

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
                <Badge className={categoryColors[peraturan.kategori] || "bg-muted text-muted-foreground"}>
                  {peraturan.kategori}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  Nomor {peraturan.nomor} Tahun {peraturan.tahun}
                </span>
              </div>
              <CardTitle className="text-2xl">{peraturan.judul}</CardTitle>
              <p className="text-muted-foreground">{peraturan.tentang}</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <Share2 className="h-4 w-4 mr-2" />
                Bagikan
              </Button>
              {peraturan.pdf_url && (
                <Button size="sm" asChild>
                  <a href={peraturan.pdf_url} target="_blank" rel="noopener noreferrer">
                    <Download className="h-4 w-4 mr-2" />
                    Download PDF
                  </a>
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
            {peraturan.pemrakarsa && (
              <div className="flex items-center gap-2">
                <Building className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">Pemrakarsa:</span>
                <span className="text-sm font-medium">{peraturan.pemrakarsa}</span>
              </div>
            )}
            {peraturan.tanggal_ditetapkan && (
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">Ditetapkan:</span>
                <span className="text-sm font-medium">{peraturan.tanggal_ditetapkan}</span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Status:</span>
              <span className="inline-flex items-center rounded-full bg-civic-emerald/10 px-2 py-0.5 text-xs font-medium text-civic-emerald">
                {peraturan.status || "Berlaku"}
              </span>
            </div>
            {peraturan.url && (
              <div className="flex items-center gap-2">
                <ExternalLink className="h-4 w-4 text-muted-foreground" />
                <a
                  href={peraturan.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-medium text-primary hover:underline"
                >
                  Lihat di Peraturan.go.id
                </a>
              </div>
            )}
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
            Daftar BAB ({babList.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {babList.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              <p>Tidak ada data BAB</p>
              <p className="text-sm mt-2">Jalankan parser service untuk mengisi data.</p>
            </div>
          ) : (
            <div className="divide-y">
              {babList.map((bab) => (
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
                      <span className="font-medium">BAB {bab.nomor_bab}</span>
                      <span className="text-muted-foreground">{bab.judul_bab}</span>
                    </div>
                  </button>
                  
                  {expandedBab === bab.id && (
                    <div className="bg-muted/30 p-4 pl-12">
                      <p className="text-sm text-muted-foreground mb-4">
                        BAB {bab.nomor_bab} - {bab.judul_bab}
                      </p>
                      <Button variant="outline" size="sm">
                        Lihat Semua Pasal
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pasal Preview */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Preview Pasal ({pasalList.length})</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {pasalList.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              <p>Tidak ada data Pasal</p>
              <p className="text-sm mt-2">Jalankan parser service untuk mengisi data.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[80px]">Pasal</TableHead>
                  <TableHead>Isi Ringkas</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pasalList.slice(0, 10).map((pasal) => (
                  <TableRow key={pasal.id} className="hover:bg-muted/50">
                    <TableCell className="font-medium">Pasal {pasal.nomor_pasal}</TableCell>
                    <TableCell className="text-muted-foreground line-clamp-2">
                      {pasal.konten_pasal || pasal.judul_pasal}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}