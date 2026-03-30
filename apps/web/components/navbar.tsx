"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Search, Menu, BookOpen } from "lucide-react";
import { useState } from "react";

export function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold text-primary">Norma</span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
            <Link
              href="/"
              className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
            >
              Home
            </Link>
            <Link
              href="/peraturan"
              className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
            >
              Peraturan
            </Link>
            <Link
              href="/tentang"
              className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
            >
              Tentang
            </Link>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="search"
                placeholder="Cari peraturan..."
                className="h-9 w-64 rounded-lg border border-input bg-muted pl-9 pr-4 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
          </div>
          <Button variant="outline" size="sm" className="hidden md:flex">
            Masuk
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="md:hidden"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            <Menu className="h-5 w-5" />
          </Button>
        </div>
      </div>

      {isMenuOpen && (
        <div className="container mx-auto border-t px-4 py-4 md:hidden">
          <div className="flex flex-col gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="search"
                placeholder="Cari peraturan..."
                className="h-10 w-full rounded-lg border border-input bg-muted pl-9 pr-4 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
            <Link
              href="/"
              className="rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted"
              onClick={() => setIsMenuOpen(false)}
            >
              Home
            </Link>
            <Link
              href="/peraturan"
              className="rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted"
              onClick={() => setIsMenuOpen(false)}
            >
              Peraturan
            </Link>
            <Link
              href="/tentang"
              className="rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted"
              onClick={() => setIsMenuOpen(false)}
            >
              Tentang
            </Link>
            <Button variant="outline" size="sm" className="w-full">
              Masuk
            </Button>
          </div>
        </div>
      )}
    </nav>
  );
}