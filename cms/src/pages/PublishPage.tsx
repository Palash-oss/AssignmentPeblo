import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { CheckCircle2, AlertTriangle, Play, History, ShieldAlert, FileText } from 'lucide-react';
import { fetchValidationReport, triggerPublish, fetchPublishRuns } from '../services/api';
import type { ValidationIssue } from '../types';

interface PublishPageProps {
  role: 'admin' | 'editor';
}

export const PublishPage: React.FC<PublishPageProps> = ({ role }) => {
  const queryClient = useQueryClient();

  const [publishing, setPublishing] = useState(false);
  const [publishMessage, setPublishMessage] = useState<string | null>(null);
  const [publishError, setPublishError] = useState<string | null>(null);

  const { data: report, isLoading: loadingReport, isError: reportError } = useQuery({
    queryKey: ['validation-report'],
    queryFn: () => fetchValidationReport(),
  });

  const { data: runs, isLoading: loadingRuns } = useQuery({
    queryKey: ['publish-runs'],
    queryFn: () => fetchPublishRuns(),
  });

  const handlePublish = async () => {
    setPublishMessage(null);
    setPublishError(null);
    setPublishing(true);

    try {
      const res = await triggerPublish();
      setPublishMessage(`Success! Published catalog. Run ID: ${res.run_id}`);
      queryClient.invalidateQueries({ queryKey: ['validation-report'] });
      queryClient.invalidateQueries({ queryKey: ['publish-runs'] });
    } catch (err: any) {
      setPublishError(err.message || 'Publish failed');
    } finally {
      setPublishing(false);
    }
  };

  const isBlocked = !report?.is_publishable;
  const isAdmin = role === 'admin';
  const canPublish = !isBlocked && isAdmin;

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2>Validation Report & Atomic Publishing</h2>
          <p className="page-desc">Audit catalog publishability, view blocking issues, and execute atomic catalog swaps.</p>
        </div>

        <div className="publish-action-box">
          <button
            className={`btn-publish ${canPublish ? 'ready' : 'blocked'}`}
            disabled={!canPublish || publishing}
            onClick={handlePublish}
          >
            <Play size={18} />
            <span>{publishing ? 'Publishing Atomic Catalog...' : 'Publish Catalog'}</span>
          </button>

          {!isAdmin && (
            <div className="publish-reason-tag warn">
              <ShieldAlert size={14} /> Only Admin role can trigger catalog publish (Current: Editor).
            </div>
          )}

          {isBlocked && (
            <div className="publish-reason-tag danger">
              <AlertTriangle size={14} /> Blocked: {report?.total_issues} validation issue(s) must be resolved.
            </div>
          )}
        </div>
      </div>

      {publishMessage && (
        <div className="banner-success">
          <CheckCircle2 size={18} />
          <span>{publishMessage}</span>
        </div>
      )}

      {publishError && (
        <div className="banner-error">
          <AlertTriangle size={18} />
          <span>{publishError}</span>
        </div>
      )}

      <div className="section-block">
        <h3 className="section-title">
          <FileText size={18} /> Live Validation Report Audit
        </h3>

        {loadingReport ? (
          <div className="state-box">Auditing catalog rules...</div>
        ) : reportError ? (
          <div className="state-box error">Error loading validation report.</div>
        ) : (
          <div className="report-dashboard">
            <div className={`report-summary-card ${report?.is_publishable ? 'clean' : 'blocked'}`}>
              <div className="summary-status">
                {report?.is_publishable ? (
                  <>
                    <CheckCircle2 size={24} className="text-success" />
                    <div>
                      <h4>Catalog Ready for Publishing</h4>
                      <p>All 4 validation check suites passed cleanly.</p>
                    </div>
                  </>
                ) : (
                  <>
                    <AlertTriangle size={24} className="text-danger" />
                    <div>
                      <h4>Publishing Blocked ({report?.total_issues} Issues)</h4>
                      <p>Fix the flagged items below in the Episodes tab before publishing.</p>
                    </div>
                  </>
                )}
              </div>
            </div>

            {report && report.total_issues > 0 && (
              <div className="issues-list-container">
                {report.issues_by_category.missing_artwork.length > 0 && (
                  <div className="issue-category-card">
                    <h4>Missing Artwork ({report.issues_by_category.missing_artwork.length})</h4>
                    <ul className="issue-list">
                      {report.issues_by_category.missing_artwork.map((item: ValidationIssue, idx: number) => (
                        <li key={idx} className="issue-item">
                          <span className="badge-ep">{item.episode_id}</span>
                          <span>{item.message}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {report.issues_by_category.missing_duration.length > 0 && (
                  <div className="issue-category-card">
                    <h4>Missing Duration ({report.issues_by_category.missing_duration.length})</h4>
                    <ul className="issue-list">
                      {report.issues_by_category.missing_duration.map((item: ValidationIssue, idx: number) => (
                        <li key={idx} className="issue-item">
                          <span className="badge-ep">{item.episode_id}</span>
                          <span>{item.message}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {report.issues_by_category.missing_section.length > 0 && (
                  <div className="issue-category-card">
                    <h4>Missing Section ({report.issues_by_category.missing_section.length})</h4>
                    <ul className="issue-list">
                      {report.issues_by_category.missing_section.map((item: ValidationIssue, idx: number) => (
                        <li key={idx} className="issue-item">
                          <span className="badge-ep">{item.show_title}</span>
                          <span>{item.message}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {report.issues_by_category.duplicate_content_group_language.length > 0 && (
                  <div className="issue-category-card highlight">
                    <h4>Duplicate (Content Group, Language) Collisions ({report.issues_by_category.duplicate_content_group_language.length})</h4>
                    <ul className="issue-list">
                      {report.issues_by_category.duplicate_content_group_language.map((item: ValidationIssue, idx: number) => (
                        <li key={idx} className="issue-item">
                          <span className="badge-ep">COLLISION</span>
                          <span>{item.message}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="section-block">
        <h3 className="section-title">
          <History size={18} /> Publish Run History
        </h3>
        {loadingRuns ? (
          <div className="state-box">Loading execution history...</div>
        ) : !runs || runs.length === 0 ? (
          <div className="state-box empty">No past publish runs recorded yet.</div>
        ) : (
          <div className="table-responsive">
            <table className="cms-table">
              <thead>
                <tr>
                  <th>Run ID</th>
                  <th>Timestamp</th>
                  <th>Published By</th>
                  <th>Status</th>
                  <th>Item Counts</th>
                  <th>Outcome / Errors</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run) => (
                  <tr key={run.id}>
                    <td className="font-mono text-xs">{run.id}</td>
                    <td>{new Date(run.published_at).toLocaleString()}</td>
                    <td><span className="user-pill">{run.published_by}</span></td>
                    <td>
                      <span className={`status-pill ${run.status}`}>
                        {run.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="font-mono text-xs">
                      {JSON.stringify(run.item_counts)}
                    </td>
                    <td className="text-xs">
                      {run.error_summary ? (
                        <span className="text-danger">{run.error_summary}</span>
                      ) : (
                        <span className="text-success">Catalog atomic swap completed clean</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
