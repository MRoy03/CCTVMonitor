export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload extends LoginPayload {
  organization_name: string;
  full_name?: string;
}

async function postAuth(path: string, body: unknown) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail ?? "Request failed");
  }
  return response.json();
}

export const login = (payload: LoginPayload) => postAuth("/api/auth/login", payload);
export const register = (payload: RegisterPayload) => postAuth("/api/auth/register", payload);
export const logout = () => postAuth("/api/auth/logout", {});
