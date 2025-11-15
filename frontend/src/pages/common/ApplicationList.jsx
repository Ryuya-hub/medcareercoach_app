import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Layout from '../../components/common/Layout';
import { applicationsAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import toast from 'react-hot-toast';
import { Edit, Trash2, Star } from 'lucide-react';

const ApplicationList = () => {
  const { isCoach } = useAuth();
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingApp, setEditingApp] = useState(null);
  const [preferenceFilter, setPreferenceFilter] = useState('');
  const [selectionStageFilter, setSelectionStageFilter] = useState('');
  const [viewMode, setViewMode] = useState('active'); // 'active' or 'history'
  const [companySearch, setCompanySearch] = useState('');
  const [formData, setFormData] = useState({
    company_name: '',
    application_date: '',
    selection_stage: '書類選考',
    status: '選考中',
    preference_rating: 3,
    next_action_date: '',
    notes: '',
    interview_questions: {},
  });
  const [currentQuestions, setCurrentQuestions] = useState('');

  const { data: applications, isLoading } = useQuery({
    queryKey: ['applications', preferenceFilter, selectionStageFilter, viewMode],
    queryFn: () => {
      const params = {};
      if (preferenceFilter) {
        params.preference_rating = parseInt(preferenceFilter);
      }
      if (selectionStageFilter) {
        params.selection_stage = selectionStageFilter;
      }
      // コーチの場合、利用者のステータスでフィルター
      if (isCoach) {
        params.client_status = viewMode === 'active' ? 'active' : 'inactive';
      }
      return applicationsAPI.getAll(params).then((res) => res.data);
    },
  });

  // 企業名検索でフィルタリング
  const filteredApplications = applications?.filter(app =>
    !companySearch || app.company_name.toLowerCase().includes(companySearch.toLowerCase())
  );

  const createMutation = useMutation({
    mutationFn: applicationsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['applications']);
      toast.success('応募を登録しました');
      closeModal();
    },
    onError: (error) => {
      console.error('応募登録エラー:', error);
      toast.error(error.response?.data?.detail || '応募登録に失敗しました');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => applicationsAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['applications']);
      toast.success('応募を更新しました');
      closeModal();
    },
    onError: (error) => {
      console.error('応募更新エラー:', error);
      toast.error(error.response?.data?.detail || '応募更新に失敗しました');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: applicationsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['applications']);
      toast.success('応募を削除しました');
    },
    onError: (error) => {
      console.error('応募削除エラー:', error);
      toast.error(error.response?.data?.detail || '応募削除に失敗しました');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    // 現在の選考段階の質問を保存
    const updatedQuestions = { ...formData.interview_questions };
    if (currentQuestions.trim()) {
      updatedQuestions[formData.selection_stage] = currentQuestions;
    }

    // 空文字列をnullに変換
    const dataToSend = {
      ...formData,
      application_date: formData.application_date || null,
      next_action_date: formData.next_action_date || null,
      preference_rating: parseInt(formData.preference_rating),
      interview_questions: updatedQuestions,
    };

    if (editingApp) {
      updateMutation.mutate({ id: editingApp.application_id, data: dataToSend });
    } else {
      createMutation.mutate(dataToSend);
    }
  };

  const handleEdit = (app) => {
    setEditingApp(app);
    const stage = app.selection_stage || '書類選考';
    setFormData({
      company_name: app.company_name || '',
      application_date: app.application_date || '',
      selection_stage: stage,
      status: app.status || '選考中',
      preference_rating: app.preference_rating || 3,
      next_action_date: app.next_action_date || '',
      notes: app.notes || '',
      interview_questions: app.interview_questions || {},
    });
    setCurrentQuestions((app.interview_questions && app.interview_questions[stage]) || '');
    setShowModal(true);
  };

  const handleDelete = (appId) => {
    if (window.confirm('この応募を削除しますか？')) {
      deleteMutation.mutate(appId);
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingApp(null);
    setCurrentQuestions('');
    setFormData({
      company_name: '',
      application_date: '',
      selection_stage: '書類選考',
      status: '選考中',
      preference_rating: 3,
      next_action_date: '',
      notes: '',
      interview_questions: {},
    });
  };

  const renderStars = (rating) => {
    return (
      <div className="flex items-center space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            size={16}
            className={star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}
          />
        ))}
      </div>
    );
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="text-center py-12">読み込み中...</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">
            {isCoach ? (viewMode === 'active' ? '進行中の応募管理' : '応募履歴') : '応募企業管理'}
          </h2>
          <div className="flex items-center space-x-3">
            {isCoach && (
              <>
                <input
                  type="text"
                  className="input w-48"
                  placeholder="企業名で検索..."
                  value={companySearch}
                  onChange={(e) => setCompanySearch(e.target.value)}
                />
                <select
                  className="input w-48"
                  value={selectionStageFilter}
                  onChange={(e) => setSelectionStageFilter(e.target.value)}
                >
                  <option value="">選考段階: すべて</option>
                  <option value="書類選考">書類選考</option>
                  <option value="一次面接">一次面接</option>
                  <option value="二次面接">二次面接</option>
                  <option value="三次面接">三次面接</option>
                  <option value="最終面接">最終面接</option>
                </select>
              </>
            )}
            <select
              className="input w-48"
              value={preferenceFilter}
              onChange={(e) => setPreferenceFilter(e.target.value)}
            >
              <option value="">志望度: すべて</option>
              <option value="5">★★★★★ (5)</option>
              <option value="4">★★★★☆ (4)</option>
              <option value="3">★★★☆☆ (3)</option>
              <option value="2">★★☆☆☆ (2)</option>
              <option value="1">★☆☆☆☆ (1)</option>
            </select>
            {!isCoach && (
              <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                新規応募登録
              </button>
            )}
          </div>
        </div>

        {isCoach && (
          <div className="flex space-x-4 border-b">
            <button
              className={`pb-2 px-4 font-medium transition-colors ${
                viewMode === 'active'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setViewMode('active')}
            >
              進行中の応募 ({applications?.filter(app => app.client?.status === 'active').length || 0})
            </button>
            <button
              className={`pb-2 px-4 font-medium transition-colors ${
                viewMode === 'history'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setViewMode('history')}
            >
              応募履歴 ({applications?.filter(app => app.client?.status === 'inactive').length || 0})
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 gap-4">
          {filteredApplications?.map((app) => (
            <div key={app.application_id} className="card">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-lg font-semibold">{app.company_name}</h3>
                    {renderStars(app.preference_rating)}
                  </div>
                  {isCoach && app.client && (
                    <p className="text-sm text-blue-600 font-medium mt-1">
                      利用者: {app.client.last_name && app.client.first_name
                        ? `${app.client.last_name} ${app.client.first_name}`
                        : app.client.name || '名前未設定'}
                    </p>
                  )}
                  <p className="text-sm text-gray-600 mt-1">
                    選考段階: {app.selection_stage}
                  </p>
                  <p className="text-sm text-gray-600">
                    応募日: {app.application_date ? new Date(app.application_date).toLocaleDateString('ja-JP') : '未設定'}
                  </p>
                  <p className="text-sm text-gray-600">
                    次回アクション予定: {app.next_action_date ? new Date(app.next_action_date).toLocaleDateString('ja-JP') : '未設定'}
                  </p>
                  {app.next_interview_date && (
                    <p className="text-sm text-gray-600">
                      次回面接: {new Date(app.next_interview_date).toLocaleDateString('ja-JP')}
                    </p>
                  )}
                  {app.notes && (
                    <p className="text-sm text-gray-600 mt-1">
                      {app.notes}
                    </p>
                  )}
                  {app.interview_questions && Object.keys(app.interview_questions).length > 0 && (
                    <div className={`mt-2 p-3 rounded-md ${isCoach ? 'bg-yellow-50 border border-yellow-200' : 'bg-blue-50'}`}>
                      <p className={`text-sm font-semibold ${isCoach ? 'text-yellow-800' : 'text-blue-700'}`}>
                        {isCoach ? '📝 利用者が記録した面接質問:' : '面接での質問:'}
                      </p>
                      {Object.entries(app.interview_questions).map(([stage, question]) => (
                        <div key={stage} className="mt-2 pl-2 border-l-2 border-gray-300">
                          <p className="text-xs font-medium text-gray-600">{stage}</p>
                          <p className="text-sm text-gray-800 mt-1">{question}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex items-center space-x-3">
                  <span className={`badge ${
                    app.status === '選考中' ? 'badge-primary' :
                    app.status === '内定' ? 'badge-success' :
                    'badge-danger'
                  }`}>
                    {app.status}
                  </span>
                  {!isCoach && (
                    <>
                      <button
                        onClick={() => handleEdit(app)}
                        className="text-blue-500 hover:text-blue-700"
                        title="編集"
                      >
                        <Edit size={20} />
                      </button>
                      <button
                        onClick={() => handleDelete(app.application_id)}
                        className="text-red-500 hover:text-red-700"
                        title="削除"
                      >
                        <Trash2 size={20} />
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
          {!filteredApplications || filteredApplications.length === 0 && (
            <p className="text-gray-500 text-center py-12">
              {companySearch ? '検索条件に一致する応募はありません' : '応募企業はありません'}
            </p>
          )}
        </div>

        {/* Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full max-h-[90vh] overflow-y-auto">
              <h3 className="text-xl font-bold mb-4">
                {editingApp ? '応募情報を編集' : '新規応募登録'}
              </h3>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="label">企業名 *</label>
                  <input
                    type="text"
                    className="input"
                    value={formData.company_name}
                    onChange={(e) => setFormData({...formData, company_name: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <label className="label">志望度 *</label>
                  <div className="flex items-center space-x-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setFormData({...formData, preference_rating: star})}
                        className="focus:outline-none transition-transform hover:scale-110"
                      >
                        <Star
                          size={28}
                          className={star <= parseInt(formData.preference_rating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}
                        />
                      </button>
                    ))}
                    <span className="ml-2 text-sm font-medium">({formData.preference_rating})</span>
                  </div>
                </div>
                <div>
                  <label className="label">応募日</label>
                  <input
                    type="date"
                    className="input"
                    value={formData.application_date}
                    onChange={(e) => setFormData({...formData, application_date: e.target.value})}
                  />
                </div>
                <div>
                  <label className="label">次回アクション予定日</label>
                  <input
                    type="date"
                    className="input"
                    value={formData.next_action_date}
                    onChange={(e) => setFormData({...formData, next_action_date: e.target.value})}
                  />
                </div>
                <div>
                  <label className="label">選考段階</label>
                  <select
                    className="input"
                    value={formData.selection_stage}
                    onChange={(e) => {
                      const newStage = e.target.value;
                      // 現在の選考段階の質問を保存
                      const updatedQuestions = { ...formData.interview_questions };
                      if (currentQuestions.trim()) {
                        updatedQuestions[formData.selection_stage] = currentQuestions;
                      }
                      setFormData({...formData, selection_stage: newStage, interview_questions: updatedQuestions});
                      // 新しい選考段階の質問を読み込む
                      setCurrentQuestions(updatedQuestions[newStage] || '');
                    }}
                  >
                    <option>書類選考</option>
                    <option>一次面接</option>
                    <option>二次面接</option>
                    <option>三次面接</option>
                    <option>最終面接</option>
                  </select>
                </div>
                <div>
                  <label className="label">ステータス</label>
                  <select
                    className="input"
                    value={formData.status}
                    onChange={(e) => setFormData({...formData, status: e.target.value})}
                  >
                    <option>選考中</option>
                    <option>内定</option>
                    <option>不合格</option>
                  </select>
                </div>
                <div>
                  <label className="label">備考</label>
                  <textarea
                    className="input"
                    rows={3}
                    value={formData.notes}
                    onChange={(e) => setFormData({...formData, notes: e.target.value})}
                    placeholder="企業に関するメモなど"
                  />
                </div>
                <div>
                  <label className="label">面接官からの質問内容 ({formData.selection_stage})</label>
                  <textarea
                    className="input"
                    rows={4}
                    value={currentQuestions}
                    onChange={(e) => setCurrentQuestions(e.target.value)}
                    placeholder={`${formData.selection_stage}で質問された内容を記録してください`}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    選考段階ごとに質問内容を記録できます。コーチも閲覧可能です。
                  </p>
                </div>
                <div className="flex justify-end space-x-3">
                  <button type="button" className="btn btn-secondary" onClick={closeModal}>
                    キャンセル
                  </button>
                  <button type="submit" className="btn btn-primary">
                    {editingApp ? '更新' : '登録'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default ApplicationList;
