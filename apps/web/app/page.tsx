import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
	Search,
	FileText,
	Scale,
	BookOpen,
	Landmark,
	ArrowRight,
} from "lucide-react";

const API_URL = process.env.API_URL || "http://localhost:8080";

const API_URL = process.env.API_URL || "http://localhost:8080";

const stats = [
	{
		label: "Total Peraturan",
		value: "12,847",
		icon: FileText,
		color: "bg-primary/10 text-primary",
	},
	{
		label: "Undang-Undang (UU)",
		value: "1,234",
		icon: Scale,
		color: "bg-civic-emerald/10 text-civic-emerald",
	},
	{
		label: "Peraturan Pemerintah (PP)",
		value: "856",
		icon: BookOpen,
		color: "bg-civic-amber/10 text-civic-amber",
	},
	{
		label: "Peraturan Presiden",
		value: "432",
		icon: Landmark,
		color: "bg-civic-teal/10 text-civic-teal",
	},
];

const categories = [
	{
		name: "Undang-Undang (UU)",
		count: "1,234",
		href: "/peraturan?kategori=UU",
	},
	{
		name: "Peraturan Pemerintah (PP)",
		count: "856",
		href: "/peraturan?kategori=PP",
	},
	{
		name: "Peraturan Presiden (Perpres)",
		count: "432",
		href: "/peraturan?kategori=Perpres",
	},
	{
		name: "Peraturan Menteri (Permen)",
		count: "2,156",
		href: "/peraturan?kategori=Permen",
	},
	{
		name: "Peraturan Daerah (Perda)",
		count: "6,789",
		href: "/peraturan?kategori=Perda",
	},
	{ name: "Lainnya", count: "1,380", href: "/peraturan?kategori=Lainnya" },
];

const categoryColors: Record<string, string> = {
	UU: "bg-primary/10 text-primary hover:bg-primary/20",
	PP: "bg-civic-emerald/10 text-civic-emerald hover:bg-civic-emerald/20",
	Perpres: "bg-civic-amber/10 text-civic-amber hover:bg-civic-amber/20",
	Permen: "bg-civic-teal/10 text-civic-teal hover:bg-civic-teal/20",
};

interface Peraturan {
	id: string;
	judul: string;
	nomor: string;
	tahun: number;
	kategori: string;
	tentang: string;
	status: string;
}

async function getRecentPeraturan(): Promise<Peraturan[]> {
<<<<<<< HEAD
	try {
		const res = await fetch(`${API_URL}/api/v1/peraturan?limit=4`, {
			cache: "no-store",
		});
		if (!res.ok) return [];
		const data = await res.json();
		return data.data || [];
	} catch {
		return [];
	}
=======
  try {
    const res = await fetch(`${API_URL}/api/v1/peraturan?limit=4`, {
      cache: "no-store",
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.data || [];
  } catch {
    return [];
  }
>>>>>>> c7e2609ffbce6d65b79334678c3bf06261b6042a
}

export default async function HomePage() {
	const recentPeraturan = await getRecentPeraturan();

	return (
		<div className="space-y-12">
			{/* Hero Section */}
			<section className="text-center py-12">
				<h1 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground mb-4">
					Database Peraturan Indonesia
				</h1>
				<p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
					Cari dan telusuri peraturan perundang-undangan Indonesia dengan mudah.
					Akses UU, PP, Perpres, Permen, dan peraturan lainnya.
				</p>

				{/* Search Box */}
				<div className="max-w-2xl mx-auto">
					<form action="/peraturan" method="GET">
						<div className="relative">
							<Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
							<Input
								type="search"
								name="search"
								placeholder="Cari peraturan berdasarkan judul, nomor, atau kata kunci..."
								className="h-14 pl-12 pr-4 text-base rounded-xl shadow-sm focus:border-primary focus:ring-primary"
							/>
							<Button
								type="submit"
								className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg"
							>
								Cari
							</Button>
						</div>
					</form>
				</div>
			</section>

			{/* Statistics */}
			<section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
				{stats.map((stat) => (
					<Card key={stat.label} className="hover:shadow-md transition-shadow">
						<CardContent className="p-6">
							<div className="flex items-center gap-4">
								<div className={`rounded-lg p-3 ${stat.color}`}>
									<stat.icon className="h-6 w-6" />
								</div>
								<div>
									<p className="text-sm font-medium text-muted-foreground">
										{stat.label}
									</p>
									<p className="text-2xl font-bold text-foreground">
										{stat.value}
									</p>
								</div>
							</div>
						</CardContent>
					</Card>
				))}
			</section>

<<<<<<< HEAD
			{/* Categories */}
			<section>
				<h2 className="text-2xl font-bold text-foreground mb-6">
					Kategori Peraturan
				</h2>
				<div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
					{categories.map((category) => (
						<Link
							key={category.name}
							href={category.href}
							className="flex items-center justify-between rounded-lg border border-border bg-card p-4 hover:border-primary hover:shadow-md transition-all"
						>
							<div>
								<p className="font-medium text-foreground">{category.name}</p>
								<p className="text-sm text-muted-foreground">
									{category.count} peraturan
								</p>
							</div>
							<ArrowRight className="h-4 w-4 text-muted-foreground" />
						</Link>
					))}
				</div>
			</section>

			{/* Recent Peraturan */}
			<section>
				<div className="flex items-center justify-between mb-6">
					<h2 className="text-2xl font-bold text-foreground">
						Peraturan Terbaru
					</h2>
					<Link
						href="/peraturan"
						className="text-sm font-medium text-primary hover:text-primary/80 flex items-center gap-1"
					>
						Lihat Semua <ArrowRight className="h-4 w-4" />
					</Link>
				</div>
				{recentPeraturan.length === 0 ? (
					<Card>
						<CardContent className="p-8 text-center">
							<p className="text-muted-foreground">
								Tidak ada data peraturan. Pastikan backend API berjalan.
							</p>
							<p className="text-sm text-muted-foreground mt-2">
								Jalankan parser service untuk mengisi data.
							</p>
						</CardContent>
					</Card>
				) : (
					<div className="grid grid-cols-1 gap-4 md:grid-cols-2">
						{recentPeraturan.map((peraturan) => (
							<Card
								key={peraturan.id}
								className="hover:shadow-md transition-shadow"
							>
								<CardHeader className="pb-3">
									<div className="flex items-start justify-between">
										<Badge
											className={
												categoryColors[peraturan.kategori] ||
												"bg-muted text-muted-foreground"
											}
										>
											{peraturan.kategori}
										</Badge>
										<span className="text-sm text-muted-foreground">
											{peraturan.tahun}
										</span>
									</div>
									<CardTitle className="text-lg line-clamp-2 mt-2">
										<Link
											href={`/peraturan/${peraturan.id}`}
											className="hover:text-primary transition-colors"
										>
											{peraturan.judul}
										</Link>
									</CardTitle>
								</CardHeader>
								<CardContent>
									<p className="text-sm text-muted-foreground line-clamp-1">
										{peraturan.tentang}
									</p>
								</CardContent>
							</Card>
						))}
					</div>
				)}
			</section>
		</div>
	);
}
=======
      {/* Recent Peraturan */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-foreground">Peraturan Terbaru</h2>
          <Link
            href="/peraturan"
            className="text-sm font-medium text-primary hover:text-primary/80 flex items-center gap-1"
          >
            Lihat Semua <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        {recentPeraturan.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <p className="text-muted-foreground">Tidak ada data peraturan. Pastikan backend API berjalan.</p>
              <p className="text-sm text-muted-foreground mt-2">
                Jalankan parser service untuk mengisi data.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {recentPeraturan.map((peraturan) => (
              <Card key={peraturan.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <Badge className={categoryColors[peraturan.kategori] || "bg-muted text-muted-foreground"}>
                      {peraturan.kategori}
                    </Badge>
                    <span className="text-sm text-muted-foreground">{peraturan.tahun}</span>
                  </div>
                  <CardTitle className="text-lg line-clamp-2 mt-2">
                    <Link
                      href={`/peraturan/${peraturan.id}`}
                      className="hover:text-primary transition-colors"
                    >
                      {peraturan.judul}
                    </Link>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground line-clamp-1">
                    {peraturan.tentang}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
>>>>>>> c7e2609ffbce6d65b79334678c3bf06261b6042a
