import { NextRequest, NextResponse } from "next/server";

import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/cookies";

export function middleware(request: NextRequest) {
  const hasToken = request.cookies.has(ACCESS_TOKEN_COOKIE);
  const { pathname } = request.nextUrl;

  if (!hasToken && pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  if (!hasToken && pathname.startsWith("/sources")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  if (hasToken && pathname === "/login") {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/sources/:path*", "/login"],
};
