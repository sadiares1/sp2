"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

const GOLD = "#d4af37";
const GREEN = "#2d6a2d";
const GREEN_LIGHT = "#4a9e4a";

export default function LoginModal() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("login");
  const [loginForm, setLoginForm] = useState({ email: "", password: "" });
  const [signupForm, setSignupForm] = useState({
    first_name: "",
    middle_name: "",
    last_name: "",
    suffix: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const API_BASE = process.env.NEXT_PUBLIC_API_URL;
  const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;

  const handleLoginSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    try {
      const response = await fetch(`${API_BASE}/api/auth/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(loginForm),
      });

      const data = await response.json();
      if (!response.ok) {
        setError(data.error || "Login failed.");
        return;
      }

      if (data?.user) {
        localStorage.setItem("authUser", JSON.stringify(data.user));

        const maxAge = (60 * 60 * 10) + (60 * 30);
        document.cookie = `auth_logged_in=1; path=/; max-age=${maxAge}; SameSite=Lax`;
        document.cookie = `auth_role=${encodeURIComponent(data.user.role || "")}; path=/; max-age=${maxAge}; SameSite=Lax`;
      }

      setSuccess("Login successful.");
      setOpen(false);

      if (data?.user?.role === "researcher") {
        router.push("/dashboard-researcher");
      }
    } catch {
      setError("Unable to connect to the server.");
    }
  };

  const handleSignupSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (!signupForm.first_name.trim() || !signupForm.last_name.trim() || !signupForm.email.trim() || !signupForm.password) {
      setError("First name, last name, email, and password are required.");
      return;
    }

    if (!PASSWORD_REGEX.test(signupForm.password)) {
      setError("Password must be at least 8 characters long and include at least 1 uppercase letter, 1 lowercase letter, and 1 number.");
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/auth/signup/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(signupForm),
      });

      const data = await response.json();
      if (!response.ok) {
        setError(data.error || "Signup failed.");
        return;
      }

      setSignupForm({
        first_name: "",
        middle_name: "",
        last_name: "",
        suffix: "",
        email: "",
        password: "",
        confirm_password: "",
      });
      setActiveTab("login");
      setSuccess("Signup successful. You can now log in.");
    } catch {
      setError("Unable to connect to the server.");
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
            size="lg"
            className="font-semibold text-sm px-7 py-2 rounded-md shadow-lg hover:scale-105 transition-transform"
            style={{ background: GOLD, color: "#1a3a1a" }}
            >
            Get Started
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-[420px] pt-8 pr-10">
        {error ? <p className="text-sm text-red-600">{error}</p> : null}
        {success ? <p className="text-sm text-green-700">{success}</p> : null}

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid grid-cols-2 w-full">
            <TabsTrigger
              value="login"
              className="data-[state=active]:text-white"
              style={{ ["--tab-active-bg"]: GREEN }}
            >
              Login
            </TabsTrigger>
            <TabsTrigger
              value="signup"
              className="data-[state=active]:text-white"
              style={{ ["--tab-active-bg"]: GREEN_LIGHT }}
            >
              Signup
            </TabsTrigger>
          </TabsList>

          <TabsContent value="login" className="mt-4">
            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="login-email">Email Address</Label>
                <Input
                  id="login-email"
                  type="email"
                  required
                  value={loginForm.email}
                  onChange={(e) => setLoginForm((prev) => ({ ...prev, email: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="login-password">Password</Label>
                <Input
                  id="login-password"
                  type="password"
                  required
                  value={loginForm.password}
                  onChange={(e) => setLoginForm((prev) => ({ ...prev, password: e.target.value }))}
                />
              </div>
              <Button type="submit" className="w-full text-white" style={{ backgroundColor: GOLD }}>
                Login
              </Button>
            </form>
          </TabsContent>

          <TabsContent value="signup" className="mt-4">
            <form onSubmit={handleSignupSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="signup-first-name">First Name<span className="text-red-500">*</span></Label>
                <Input
                  id="signup-first-name"
                  required
                  value={signupForm.first_name}
                  onChange={(e) => setSignupForm((prev) => ({ ...prev, first_name: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="signup-middle-name">Middle Name (Optional)</Label>
                <Input
                  id="signup-middle-name"
                  value={signupForm.middle_name}
                  onChange={(e) => setSignupForm((prev) => ({ ...prev, middle_name: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="signup-last-name">Last Name<span className="text-red-500">*</span></Label>
                <Input
                  id="signup-last-name"
                  required
                  value={signupForm.last_name}
                  onChange={(e) => setSignupForm((prev) => ({ ...prev, last_name: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="signup-suffix">Suffix (Optional)</Label>
                <Input
                  id="signup-suffix"
                  value={signupForm.suffix}
                  onChange={(e) => setSignupForm((prev) => ({ ...prev, suffix: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="signup-email">Email Address<span className="text-red-500">*</span></Label>
                <Input
                  id="signup-email"
                  type="email"
                  required
                  value={signupForm.email}
                  onChange={(e) => setSignupForm((prev) => ({ ...prev, email: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="signup-password">Password<span className="text-red-500">*</span></Label>
                <Input
                  id="signup-password"
                  type="password"
                  required
                  value={signupForm.password}
                  onChange={(e) => setSignupForm((prev) => ({ ...prev, password: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="signup-confirm">Confirm Password<span className="text-red-500">*</span></Label>
                <Input
                  id="signup-confirm"
                  type="password"
                  required
                  value={signupForm.confirm_password}
                  onChange={(e) => setSignupForm((prev) => ({ ...prev, confirm_password: e.target.value }))}
                />
              </div>
              <Button type="submit" className="w-full text-white" style={{ backgroundColor: GREEN }}>
                Signup
              </Button>
            </form>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}