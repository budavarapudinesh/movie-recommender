"use client";

import { useState, useEffect, useCallback } from "react";
import api, { getMe } from "@/lib/api";
import { isAuthenticated as getAuthFlag, removeAuthFlag } from "@/lib/auth";

interface User {
  id: number;
  username: string;
  email: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    const hasAuthFlag = getAuthFlag();
    if (!hasAuthFlag) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const res = await getMe();
      setUser(res.data);
    } catch {
      removeAuthFlag();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const logout = async () => {
    try {
      await api.post("/users/logout");
    } catch (e) {
      console.error(e);
    }
    removeAuthFlag();
    setUser(null);
    window.location.href = "/";
  };

  return { user, loading, logout, refetch: fetchUser };
}
