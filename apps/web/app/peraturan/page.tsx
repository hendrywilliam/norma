"use client";

import { Suspense } from "react";
import PeraturanListContent from "./content";

export default function PeraturanListPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
      </div>
    }>
      <PeraturanListContent />
    </Suspense>
  );
}