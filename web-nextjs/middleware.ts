import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isLoggedIn = request.cookies.get("auth_logged_in")?.value === "1";
  const role = request.cookies.get("auth_role")?.value;

  const isResearcherPath = pathname.startsWith("/dashboard-researcher");
  const isPassportDataPath = pathname.startsWith("/passport-data");

  const isProtectedPath = isResearcherPath || isPassportDataPath;

  if (isProtectedPath && !isLoggedIn) {
    const url = request.nextUrl.clone();
    url.pathname = "/";
    return NextResponse.redirect(url);
  }

  if (isResearcherPath && role !== "researcher") {
    const url = request.nextUrl.clone();
    url.pathname = "/";
    return NextResponse.redirect(url);
  }

  if (pathname === "/" && isLoggedIn && role === "researcher") {
    const url = request.nextUrl.clone();
    url.pathname = "/dashboard-researcher";
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/", "/dashboard-researcher/:path*", "/passport-data/:path*"],
};
