import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // ローカルストレージからユーザー情報を読み込む
    const storedUser = localStorage.getItem('user');
    const token = localStorage.getItem('access_token');

    if (storedUser && token) {
      setUser(JSON.parse(storedUser));
      // トークンの検証
      authAPI.verify().catch(() => {
        logout();
      });
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await authAPI.login({ email, password });
      const { access_token, user_type, user_id, role } = response.data;

      localStorage.setItem('access_token', access_token);
      const userData = { user_id, email, user_type, role };
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);

      toast.success('ログインしました');
      return userData;
    } catch (error) {
      toast.error('ログインに失敗しました');
      throw error;
    }
  };

  const register = async (data) => {
    try {
      const response = await authAPI.register(data);
      const { access_token, user_type, user_id, role } = response.data;

      localStorage.setItem('access_token', access_token);
      const userData = { user_id, email: data.email, user_type, role };
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);

      toast.success('登録が完了しました');
      return userData;
    } catch (error) {
      toast.error('登録に失敗しました');
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
    toast.success('ログアウトしました');
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    isCoach: user?.user_type === 'coach',
    isClient: user?.user_type === 'client',
    isSuperAdmin: user?.role === 'super_admin',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
