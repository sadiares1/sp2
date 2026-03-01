"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import About from "@/components/About";

const BG = "#f7f9f4";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const redirectIfResearcher = (rawUser: string | null) => {
      if (!rawUser) {
        return;
      }

      try {
        const user = JSON.parse(rawUser);
        if (user?.role === "researcher") {
          router.replace("/dashboard-researcher");
        }
      } catch {
      }
    };

    redirectIfResearcher(localStorage.getItem("authUser"));

    const onStorage = (event: StorageEvent) => {
      if (event.key !== "authUser") {
        return;
      }
      redirectIfResearcher(event.newValue);
    };

    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, [router]);

  return (
    <main className="min-h-screen font-sans" style={{ background: BG, fontFamily: "'Segoe UI', sans-serif" }}>
      <Navbar />
      <Hero />
      <Features />
      <About />
    </main>
  );
}