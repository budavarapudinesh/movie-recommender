"use client";

import { useState, useEffect, useCallback } from "react";
import { getMe } from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";

interface User {
  id: number;
  username: string;
  email: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    const token = getToken();
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const res = await getMe();
      setUser(res.data);
    } catch {
      removeToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const logout = () => {
    removeToken();
    setUser(null);
    window.location.href = "/";
  };

  return { user, loading, logout, refetch: fetchUser };
}
