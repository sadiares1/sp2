"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const GREEN_LIGHT = "#4a9e4a";

function SidebarLink({ href, label, isActive, isNested = false }) {
  return (
    <Link
      href={href}
      className={`block rounded-md px-3 py-2 text-sm font-medium transition-colors ${isNested ? "ml-3" : ""}`}
      style={{
        backgroundColor: isActive ? "rgba(255, 255, 255, 0.2)" : "transparent",
        color: "#ffffff",
      }}
    >
      {label}
    </Link>
  );
}

export default function Sidebar({ className = "" }) {
  const pathname = usePathname();
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    try {
      const rawUser = localStorage.getItem("authUser");
      if (!rawUser) {
        setIsAdmin(false);
        return;
      }

      const user = JSON.parse(rawUser);
      setIsAdmin(user?.role === "admin");
    } catch {
      setIsAdmin(false);
    }
  }, []);

  const topLinks = useMemo(
    () => [
      { href: "/dashboard-researcher", label: "Dashboard" },
      { href: "/passport-data", label: "Passport Data" },
      { href: "/characterization-data", label: "Characterization Data" },
      { href: "/inventory", label: "Inventory" },
    ],
    []
  );

  const bottomLinks = useMemo(
    () => [
      { href: "/viability-test", label: "Viability Test" },
      { href: "/regeneration-record", label: "Regeneration Record" },
    ],
    []
  );

  const inventoryLinks = useMemo(
    () => [
      { href: "/customers", label: "Customers" },
      { href: "/products", label: "Products" },
      { href: "/requests", label: "Requests" },
    ],
    []
  );

  return (
    <aside
      className={`w-64 min-h-screen p-4 ${className}`}
      style={{ backgroundColor: GREEN_LIGHT, color: "#ffffff" }}
    >
      <nav className="space-y-1">
        {topLinks.map((link) => (
          <SidebarLink
            key={link.href}
            href={link.href}
            label={link.label}
            isActive={pathname === link.href}
          />
        ))}

        <div className="space-y-1 pt-1">
          {inventoryLinks.map((link) => (
            <SidebarLink
              key={link.href}
              href={link.href}
              label={link.label}
              isActive={pathname === link.href}
              isNested
            />
          ))}
        </div>

        {bottomLinks.map((link) => (
          <SidebarLink
            key={link.href}
            href={link.href}
            label={link.label}
            isActive={pathname === link.href}
          />
        ))}

        {isAdmin ? (
          <SidebarLink
            href="/user-management"
            label="User Management"
            isActive={pathname === "/user-management"}
          />
        ) : null}
      </nav>
    </aside>
  );
}
