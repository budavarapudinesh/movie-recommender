"use client";

export function setAuthFlag() {
  localStorage.setItem("auth_flag", "true");
}

export function removeAuthFlag() {
  localStorage.removeItem("auth_flag");
}

export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("auth_flag");
}
