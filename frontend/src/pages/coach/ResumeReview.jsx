import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Layout from '../../components/common/Layout';
import { resumesAPI } from '../../services/api';
import toast from 'react-hot-toast';

const ResumeReview = () => {
  const queryClient = useQueryClient();
  const [selectedResume, setSelectedResume] = useState(null);
  const [comment, setComment] = useState('');

  const { data: pendingResumes } = useQuery({
    queryKey: ['pendingResumes'],
    queryFn: () => resumesAPI.getPendingResumes().then((res) => res.data),
  });

  const { data: resumeDetail } = useQuery({
    queryKey: ['resume', selectedResume],
    queryFn: () => resumesAPI.getById(selectedResume).then((res) => res.data),
    enabled: !!selectedResume,
  });

  const createReviewMutation = useMutation({
    mutationFn: ({ resumeId, data }) => resumesAPI.createReview(resumeId, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['resume', selectedResume]);
      toast.success('添削を開始しました');
    },
  });

  const completeReviewMutation = useMutation({
    mutationFn: resumesAPI.completeReview,
    onSuccess: () => {
      queryClient.invalidateQueries(['pendingResumes']);
      queryClient.invalidateQueries(['resume', selectedResume]);
      toast.success('添削を完了しました');
      setSelectedResume(null);
      setComment('');
    },
  });

  const deleteResumeMutation = useMutation({
    mutationFn: resumesAPI.deleteByCoach,
    onSuccess: () => {
      queryClient.invalidateQueries(['pendingResumes']);
      toast.success('職務経歴書を削除しました');
      setSelectedResume(null);
    },
  });

  const handleSelectResume = (resumeId) => {
    setSelectedResume(resumeId);
  };

  const handleStartReview = () => {
    if (!selectedResume) return;

    createReviewMutation.mutate({
      resumeId: selectedResume,
      data: { review_status: 'in_progress', overall_comment: comment },
    });
  };

  const handleCompleteReview = async () => {
    if (!selectedResume || !resumeDetail) return;

    // レビューが存在しない場合は先に作成
    if (!resumeDetail.reviews || resumeDetail.reviews.length === 0) {
      try {
        await createReviewMutation.mutateAsync({
          resumeId: selectedResume,
          data: { review_status: 'in_progress', overall_comment: comment },
        });
        // レビューが作成されたら、再度resumeDetailを取得する必要があるため、
        // 少し待ってから完了処理を実行
        setTimeout(async () => {
          const updatedResume = await resumesAPI.getById(selectedResume).then((res) => res.data);
          if (updatedResume.reviews && updatedResume.reviews.length > 0) {
            completeReviewMutation.mutate(updatedResume.reviews[0].review_id);
          }
        }, 500);
      } catch (error) {
        toast.error('添削の開始に失敗しました');
      }
    } else {
      // レビューが既に存在する場合は完了
      completeReviewMutation.mutate(resumeDetail.reviews[0].review_id);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">職務経歴書添削</h2>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 全ての職務経歴書リスト */}
          <div className="lg:col-span-1 space-y-4">
            <h3 className="text-lg font-semibold">職務経歴書一覧 ({pendingResumes?.length || 0}件)</h3>
            <div className="space-y-2">
              {pendingResumes?.map((resume) => (
                <div
                  key={resume.resume_id}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                    selectedResume === resume.resume_id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-primary-300'
                  }`}
                  onClick={() => handleSelectResume(resume.resume_id)}
                >
                  <div className="flex justify-between items-start">
                    <p className="font-medium">職務経歴書 v{resume.version_number}</p>
                    <span className={`badge text-xs ${
                      resume.status === 'draft' ? 'badge-warning' :
                      resume.status === 'submitted' ? 'badge-primary' :
                      resume.status === 'reviewed' ? 'badge-success' :
                      'badge-secondary'
                    }`}>
                      {resume.status === 'draft' ? '下書き' :
                       resume.status === 'submitted' ? '提出済' :
                       resume.status === 'reviewed' ? '添削済' :
                       resume.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">
                    作成: {new Date(resume.created_at).toLocaleDateString('ja-JP')}
                  </p>
                  {resume.submitted_at && (
                    <p className="text-sm text-gray-600">
                      提出: {new Date(resume.submitted_at).toLocaleDateString('ja-JP')}
                    </p>
                  )}
                </div>
              ))}
              {!pendingResumes || pendingResumes.length === 0 && (
                <p className="text-gray-500 text-center py-4">職務経歴書がありません</p>
              )}
            </div>
          </div>

          {/* 添削エリア */}
          <div className="lg:col-span-2">
            {resumeDetail ? (
              <div className="card space-y-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-bold">職務経歴書 バージョン {resumeDetail.version_number}</h3>
                    <p className="text-gray-600">作成日: {new Date(resumeDetail.created_at).toLocaleDateString('ja-JP')}</p>
                  </div>
                  <button
                    className="btn btn-sm btn-danger"
                    onClick={() => {
                      if (window.confirm('この職務経歴書を削除してもよろしいですか？')) {
                        deleteResumeMutation.mutate(resumeDetail.resume_id);
                      }
                    }}
                    disabled={deleteResumeMutation.isLoading}
                  >
                    削除
                  </button>
                </div>

                {/* 職務経歴書内容 */}
                <div className="space-y-2">
                  <h4 className="font-semibold">内容</h4>
                  <div className="bg-gray-50 p-4 rounded-md">
                    <p className="whitespace-pre-wrap font-mono text-sm">{resumeDetail.content || '（内容なし）'}</p>
                  </div>
                </div>

                {/* 添削履歴 */}
                {resumeDetail.reviews && resumeDetail.reviews.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-semibold">添削履歴 ({resumeDetail.reviews.length}件)</h4>
                    <div className="space-y-3">
                      {resumeDetail.reviews.map((review, index) => (
                        <div key={review.review_id} className="bg-blue-50 p-4 rounded-md border border-blue-200">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <p className="font-medium text-blue-900">
                                コーチ: {review.coach?.name || `${review.coach?.last_name || ''} ${review.coach?.first_name || ''}`.trim() || '不明'}
                              </p>
                              <p className="text-sm text-gray-600">
                                {new Date(review.created_at).toLocaleString('ja-JP')}
                              </p>
                            </div>
                            <span className={`badge text-xs ${
                              review.review_status === 'completed' ? 'badge-success' :
                              review.review_status === 'in_progress' ? 'badge-warning' :
                              'badge-secondary'
                            }`}>
                              {review.review_status === 'completed' ? '完了' :
                               review.review_status === 'in_progress' ? '進行中' :
                               review.review_status}
                            </span>
                          </div>
                          {review.overall_comment && (
                            <p className="text-sm text-gray-700 whitespace-pre-wrap">{review.overall_comment}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* コメント入力 */}
                <div className="space-y-2">
                  <h4 className="font-semibold">総合コメント</h4>
                  <textarea
                    rows={6}
                    className="input"
                    placeholder="添削コメントを入力..."
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                  />
                </div>

                {/* アクション */}
                <div className="flex justify-end space-x-3">
                  <button className="btn btn-secondary" onClick={() => setSelectedResume(null)}>
                    キャンセル
                  </button>
                  {resumeDetail.reviews && resumeDetail.reviews.length > 0 ? (
                    <button
                      className="btn btn-primary"
                      onClick={handleCompleteReview}
                      disabled={completeReviewMutation.isLoading}
                    >
                      {completeReviewMutation.isLoading ? '完了中...' : '添削完了'}
                    </button>
                  ) : (
                    <button
                      className="btn btn-success"
                      onClick={handleStartReview}
                      disabled={createReviewMutation.isLoading}
                    >
                      {createReviewMutation.isLoading ? '開始中...' : '添削開始'}
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <div className="card text-center py-12 text-gray-500">
                左から職務経歴書を選択してください
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ResumeReview;
