import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/cookies";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

/**
 * Proxies every frontend API call to the FastAPI backend, attaching the
 * access token from the httpOnly cookie as an Authorization header. The
 * JWT never reaches client-side JS this way.
 */
async function proxy(request: NextRequest, segments: string[]) {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get(ACCESS_TOKEN_COOKIE)?.value;

  const url = new URL(`/api/v1/${segments.join("/")}`, BACKEND_URL);
  url.search = request.nextUrl.search;

  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);
  if (accessToken) headers.set("authorization", `Bearer ${accessToken}`);

  const hasBody = !["GET", "HEAD"].includes(request.method);

  const response = await fetch(url, {
    method: request.method,
    headers,
    body: hasBody ? await request.arrayBuffer() : undefined,
  });

  const responseContentType = response.headers.get("content-type") ?? "application/json";
  const payload = await response.arrayBuffer();

  return new NextResponse(payload, {
    status: response.status,
    headers: { "content-type": responseContentType },
  });
}

type RouteContext = { params: Promise<{ path: string[] }> };

export async function GET(request: NextRequest, context: RouteContext) {
  return proxy(request, (await context.params).path);
}

export async function POST(request: NextRequest, context: RouteContext) {
  return proxy(request, (await context.params).path);
}

export async function PATCH(request: NextRequest, context: RouteContext) {
  return proxy(request, (await context.params).path);
}

export async function DELETE(request: NextRequest, context: RouteContext) {
  return proxy(request, (await context.params).path);
}
