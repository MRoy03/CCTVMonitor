export const ACCESS_TOKEN_COOKIE = "cip_access_token";
export const REFRESH_TOKEN_COOKIE = "cip_refresh_token";

export const authCookieOptions = {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax" as const,
  path: "/",
};
