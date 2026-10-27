import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { ACCESS_TOKEN_COOKIE, authCookieOptions, REFRESH_TOKEN_COOKIE } from "@/lib/auth/cookies";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest) {
  const body = await request.json();

  const response = await fetch(`${BACKEND_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Login failed" }));
    return NextResponse.json(error, { status: response.status });
  }

  const { access_token, refresh_token } = await response.json();
  const cookieStore = await cookies();
  cookieStore.set(ACCESS_TOKEN_COOKIE, access_token, authCookieOptions);
  cookieStore.set(REFRESH_TOKEN_COOKIE, refresh_token, authCookieOptions);

  return NextResponse.json({ ok: true });
}
