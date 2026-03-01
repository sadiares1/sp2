"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/Sidebar";

export default function DashboardResearcherPage() {
  const router = useRouter();
  const API_BASE = process.env.NEXT_PUBLIC_API_URL;
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    const authorize = (rawUser: string | null) => {
      if (!rawUser) {
        setAuthorized(false);
        router.replace("/");
        return;
      }

      try {
        const user = JSON.parse(rawUser);
        if (user?.role !== "researcher") {
          setAuthorized(false);
          localStorage.removeItem("authUser");
          router.replace("/");
          return;
        }
        setAuthorized(true);
      } catch {
        setAuthorized(false);
        localStorage.removeItem("authUser");
        router.replace("/");
      }
    };

    authorize(localStorage.getItem("authUser"));

    const onStorage = (event: StorageEvent) => {
      if (event.key !== "authUser") {
        return;
      }
      authorize(event.newValue);
    };

    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, [router]);

  const handleLogout = async () => {
    try {
      await fetch(`${API_BASE}/api/auth/logout/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
    } catch {
    } finally {
      localStorage.removeItem("authUser");
      document.cookie = "auth_logged_in=; path=/; max-age=0; SameSite=Lax";
      document.cookie = "auth_role=; path=/; max-age=0; SameSite=Lax";
      router.push("/");
    }
  };

  if (!authorized) {
    return null;
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="flex min-h-screen">
        <Sidebar />

        <div className="flex-1 p-6 md:p-10">
          <div className="mx-auto max-w-6xl space-y-6">
            <header className="flex items-start justify-between gap-4">
              <div className="space-y-1">
                <h1 className="text-2xl font-semibold tracking-tight">Researcher Dashboard</h1>
                <p className="text-muted-foreground text-sm">Welcome to your workspace.</p>
              </div>
              <Button onClick={handleLogout} variant="destructive">
                Logout
              </Button>
            </header>

            <section className="grid gap-4 md:grid-cols-3">
              <Card>
                <CardHeader>
                  <CardTitle>Passport Records</CardTitle>
                  <CardDescription>Total entries available in the system.</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold">0</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Pending Requests</CardTitle>
                  <CardDescription>Records waiting for your review.</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold">0</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Recent Uploads</CardTitle>
                  <CardDescription>Newly added media and related files.</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold">0</p>
                </CardContent>
              </Card>
            </section>

            <section className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                  <CardDescription>Latest updates will appear here.</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground text-sm">No activity yet.</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Quick Notes</CardTitle>
                  <CardDescription>Track reminders for your work.</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground text-sm">No notes yet.</p>
                </CardContent>
              </Card>
            </section>
          </div>
        </div>
      </div>
    </main>
  );
}
