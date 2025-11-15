import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import toast from 'react-hot-toast';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    furigana: '',
    phone: '',
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      toast.error('パスワードが一致しません');
      return;
    }

    setLoading(true);

    try {
      const { confirmPassword, ...registerData } = formData;
      const response = await api.post('/api/auth/register/client', registerData);
      const { access_token, user_type, user_id } = response.data;

      localStorage.setItem('access_token', access_token);
      const userData = { user_id, email: registerData.email, user_type };
      localStorage.setItem('user', JSON.stringify(userData));

      toast.success('登録が完了しました');
      navigate('/client/dashboard');
    } catch (error) {
      console.error('Register error:', error);
      toast.error(error.response?.data?.detail || '登録に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
        <div>
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            利用者アカウント登録
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            転職支援を受けるためのアカウントを作成します
          </p>
        </div>
        <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="name" className="label">
              氏名
            </label>
            <input
              id="name"
              name="name"
              type="text"
              required
              className="input"
              value={formData.name}
              onChange={handleChange}
            />
          </div>

          <div>
            <label htmlFor="furigana" className="label">
              ふりがな
            </label>
            <input
              id="furigana"
              name="furigana"
              type="text"
              className="input"
              value={formData.furigana}
              onChange={handleChange}
            />
          </div>

          <div>
            <label htmlFor="email" className="label">
              メールアドレス
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              className="input"
              value={formData.email}
              onChange={handleChange}
            />
          </div>

          <div>
            <label htmlFor="phone" className="label">
              電話番号
            </label>
            <input
              id="phone"
              name="phone"
              type="tel"
              className="input"
              value={formData.phone}
              onChange={handleChange}
            />
          </div>

          <div>
            <label htmlFor="password" className="label">
              パスワード
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              className="input"
              value={formData.password}
              onChange={handleChange}
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="label">
              パスワード（確認）
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              required
              className="input"
              value={formData.confirmPassword}
              onChange={handleChange}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn btn-primary disabled:opacity-50"
          >
            {loading ? '登録中...' : '登録'}
          </button>

          <div className="text-center">
            <Link to="/login" className="text-sm text-primary-600 hover:text-primary-500">
              既にアカウントをお持ちの方
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;
