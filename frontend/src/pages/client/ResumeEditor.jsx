import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Layout from '../../components/common/Layout';
import { resumesAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import toast from 'react-hot-toast';
import { User, Calendar } from 'lucide-react';

const ResumeEditor = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [formData, setFormData] = useState({
    content: '',
    template_type: 'standard',
  });

  const { data: resumes, isLoading: resumesLoading } = useQuery({
    queryKey: ['my-resumes'],
    queryFn: () => resumesAPI.getMe().then((res) => res.data),
    enabled: !!user,
  });

  // 添削履歴を取得（最新の職務経歴書の場合のみ）
  const latestResume = resumes?.[0];
  const { data: reviews } = useQuery({
    queryKey: ['resume-reviews', latestResume?.resume_id],
    queryFn: () => resumesAPI.getReviews(latestResume.resume_id).then((res) => res.data),
    enabled: !!latestResume?.resume_id,
  });

  // resumesがロードされたらformDataを更新
  useEffect(() => {
    if (resumes && resumes.length > 0) {
      const latestResume = resumes.find(r => r.status === 'draft') || resumes[0];
      setFormData({
        content: latestResume.content || '',
        template_type: latestResume.template_type || 'standard',
      });
    }
  }, [resumes]);

  const createMutation = useMutation({
    mutationFn: resumesAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['my-resumes']);
      toast.success('職務経歴書を作成しました');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => resumesAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['my-resumes']);
      toast.success('職務経歴書を更新しました');
    },
  });

  const submitMutation = useMutation({
    mutationFn: resumesAPI.submit,
    onSuccess: () => {
      queryClient.invalidateQueries(['my-resumes']);
      toast.success('職務経歴書を提出しました');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const latestDraftResume = resumes?.find(r => r.status === 'draft');

    if (latestDraftResume) {
      updateMutation.mutate({ id: latestDraftResume.resume_id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const deleteMutation = useMutation({
    mutationFn: resumesAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['my-resumes']);
      toast.success('職務経歴書を削除しました');
    },
  });

  const applyReviewMutation = useMutation({
    mutationFn: ({ resumeId, reviewId }) => resumesAPI.applyReview(resumeId, reviewId),
    onSuccess: () => {
      queryClient.invalidateQueries(['my-resumes']);
      toast.success('添削を反映しました');
    },
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">職務経歴書</h2>
          {resumes?.[0] && resumes[0].status === 'draft' && (
            <button
              className="btn btn-primary"
              onClick={() => submitMutation.mutate(resumes[0].resume_id)}
            >
              コーチに提出
            </button>
          )}
        </div>

        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="label">職務経歴書</label>
              <textarea
                name="content"
                rows={20}
                className="input font-mono"
                value={formData.content}
                onChange={handleChange}
                placeholder="【役割】&#10;&#10;【業務内容】&#10;&#10;【主な業績と成果】&#10;&#10;【業務で使用しているツール】&#10;&#10;【スキルセット】"
              />
            </div>

            <div className="flex justify-end space-x-3">
              <button type="submit" className="btn btn-primary">
                保存
              </button>
            </div>
          </form>
        </div>

        {/* 添削履歴セクション */}
        {reviews && reviews.length > 0 && (
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">添削履歴 ({reviews.length}件)</h3>
            <div className="space-y-4">
              {reviews.map((review) => (
                <div key={review.review_id} className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center space-x-2">
                      <User size={18} className="text-primary-600" />
                      <span className="font-medium">
                        {review.coach?.name || `${review.coach?.last_name || ''} ${review.coach?.first_name || ''}`.trim() || 'コーチ'}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Calendar size={16} />
                      <span>{new Date(review.created_at).toLocaleDateString('ja-JP')}</span>
                    </div>
                  </div>
                  {review.overall_comment && (
                    <div className="bg-gray-50 p-3 rounded-md mb-3">
                      <p className="text-sm whitespace-pre-wrap">{review.overall_comment}</p>
                    </div>
                  )}
                  <div className="flex justify-between items-center">
                    <span className={`badge text-xs ${
                      review.review_status === 'in_progress' ? 'badge-warning' :
                      review.review_status === 'completed' ? 'badge-success' :
                      'badge-secondary'
                    }`}>
                      {review.review_status === 'in_progress' ? '添削中' :
                       review.review_status === 'completed' ? '完了' :
                       review.review_status}
                    </span>
                    {review.review_status === 'completed' && review.overall_comment && (
                      <button
                        className="btn btn-sm btn-primary"
                        onClick={() => applyReviewMutation.mutate({ resumeId: latestResume.resume_id, reviewId: review.review_id })}
                        disabled={applyReviewMutation.isLoading}
                      >
                        添削を反映
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default ResumeEditor;
