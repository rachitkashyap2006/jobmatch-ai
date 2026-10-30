
import { useState, useRef } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";
const MAX_FILE_SIZE = 5 * 1024 * 1024;

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

function getScoreLevel(score) {
  if (score >= 70) return "good";
  if (score >= 40) return "moderate";
  return "low";
}

function App() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [jobResults, setJobResults] = useState(null);
  const [jobProfile, setJobProfile] = useState(null);
  const [jobWarnings, setJobWarnings] = useState([]);
  const [recommender, setRecommender] = useState(null);

  const [loading, setLoading] = useState(false);
  const [jobLoading, setJobLoading] = useState(false);
  const [error, setError] = useState("");
  const [jobError, setJobError] = useState("");

  // YouTube learning resources states
  const [learningResources, setLearningResources] = useState(null);
  const [learningLoading, setLearningLoading] = useState(false);
  const [learningError, setLearningError] = useState("");

  const [dragActive, setDragActive] = useState(false);
  const resultsRef = useRef(null);
  const fileInputRef = useRef(null);

  function validateAndSetFile(file) {
    if (!file) return;

    if (file.type !== "application/pdf") {
      setError("Only PDF files are supported. Please choose a .pdf file.");
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setError(
        `File is too large (${formatFileSize(file.size)}). Maximum size is 5 MB.`
      );
      return;
    }

    setResume(file);
    setResult(null);
    setJobResults(null);
    setJobProfile(null);
    setJobWarnings([]);
    setLearningResources(null);
    setLearningError("");
    setError("");
    setJobError("");
  }

  function handleResumeChange(event) {
    validateAndSetFile(event.target.files?.[0]);
  }

  function removeFile() {
    setResume(null);
    setResult(null);
    setJobResults(null);
    setJobProfile(null);
    setJobWarnings([]);
    setLearningResources(null);
    setLearningError("");
    setError("");
    setJobError("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }

  function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }

  function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    validateAndSetFile(e.dataTransfer.files?.[0]);
  }

  async function analyzeResume(event) {
    event.preventDefault();

    if (!resume) {
      setError("Please upload your resume PDF.");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Please enter a job description.");
      return;
    }

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("job_description", jobDescription);

    setLoading(true);
    setError("");
    setResult(null);
    setLearningResources(null);
    setLearningError("");

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Analysis failed.");
      }

      setResult(data);

      setTimeout(() => {
        resultsRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }, 100);
    } catch (err) {
      setError(
        err.message ||
          "Could not connect to the backend. Check whether FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  }

  async function findRecommendedJobs() {
    if (!resume) {
      setJobError("Please upload your resume PDF first.");
      return;
    }

    const formData = new FormData();
    formData.append("resume", resume);

    setJobLoading(true);
    setJobError("");
    setJobResults(null);

    try {
      const response = await fetch(`${API_BASE_URL}/recommend-jobs`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Job recommendations failed.");
      }

      setJobResults(data.recommended_jobs || []);
      setJobProfile(data.candidate_profile || null);
      setJobWarnings(data.data_quality_warnings || []);
      setRecommender(data.recommender || null);
    } catch (err) {
      setJobError(
        err.message ||
          "Could not connect to the backend. Check whether FastAPI is running."
      );
    } finally {
      setJobLoading(false);
    }
  }

  // Fetch YouTube tutorials for missing skills
  async function findLearningResources() {
    const missingSkills = result?.missing_skills || [];

    if (missingSkills.length === 0) {
      setLearningError("No missing skills found to search for.");
      return;
    }

    setLearningLoading(true);
    setLearningError("");
    setLearningResources(null);

    try {
      // Remove duplicate skills and search for at most five.
      const skills = [
        ...new Set(
          missingSkills.filter(
            (skill) => typeof skill === "string" && skill.trim()
          )
        ),
      ].slice(0, 5);

      const response = await fetch(
        `${API_BASE_URL}/learning-resources`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ skills }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Could not fetch YouTube learning resources."
        );
      }

      setLearningResources(data.resources || {});
    } catch (err) {
      setLearningError(
        err.message ||
          "Could not connect to the backend. Check whether FastAPI is running."
      );
    } finally {
      setLearningLoading(false);
    }
  }

  return (
    <main className="app">
      <header className="header">
        <a className="brand" href="#top" aria-label="JobMatch AI home">
          <span className="brand-icon" aria-hidden="true">
            <span />
            <span />
            <span />
          </span>
          <span>JobMatch<span className="brand-light"> AI</span></span>
        </a>
        <nav className="header-nav" aria-label="Main navigation">
          <a href="#analyzer">Resume analysis</a>
          <a href="#jobs">Job matches</a>
          <a className="header-cta" href="#analyzer">
            Get started <span aria-hidden="true">↗</span>
          </a>
        </nav>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <span className="hero-eyebrow">
            <span className="status-dot" />
            A clearer view of your next move
          </span>
          <h1>
            Know where you stand.
            <br />
            <span>See where you could go.</span>
          </h1>
          <p>
            Put your experience beside the role you want. Get a grounded view
            of your fit, the skills to build, and the jobs worth exploring.
          </p>
          <a className="hero-link" href="#analyzer">
            Start with your resume <span aria-hidden="true">↓</span>
          </a>
        </div>
        <aside className="hero-note" aria-label="How JobMatch works">
          <span className="hero-note-label">A practical way forward</span>
          <div className="hero-note-step">
            <span>01</span>
            <p>See how your experience maps to the role.</p>
          </div>
          <div className="hero-note-step">
            <span>02</span>
            <p>Focus on the skills that would move you forward.</p>
          </div>
          <div className="hero-note-rule" />
          <span className="hero-note-foot">Your resume stays on this app's backend.</span>
        </aside>
      </section>

      {/* ─── Upload & Analysis Form ─── */}

      <form className="analyzer" id="analyzer" onSubmit={analyzeResume}>
        <section className="panel upload-panel">
          <div className="section-heading">
            <span className="step">01</span>
            <div>
              <h2>Upload your resume</h2>
              <p>PDF with selectable text. Maximum 5 MB.</p>
            </div>
          </div>

          {resume ? (
            <div className="file-info">
              <div className="file-info-icon">PDF</div>
              <div className="file-info-details">
                <strong>{resume.name}</strong>
                <span>{formatFileSize(resume.size)}</span>
              </div>
              <button
                type="button"
                className="file-remove"
                onClick={removeFile}
                aria-label="Remove file"
              >
                ✕
              </button>
            </div>
          ) : (
            <label
              className={`upload-area${dragActive ? " drag-active" : ""}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleResumeChange}
              />
              <span className="upload-icon">↑</span>
              <strong>
                {dragActive
                  ? "Drop your PDF here"
                  : "Click or drag your resume here"}
              </strong>
              <span>PDF format only</span>
            </label>
          )}
        </section>

        <section className="panel description-panel">
          <div className="section-heading">
            <span className="step">02</span>
            <div>
              <h2>Paste the job description</h2>
              <p>
                Required for resume analysis and skill-gap detection.
              </p>
            </div>
          </div>

          <textarea
            value={jobDescription}
            onChange={(event) => {
              setJobDescription(event.target.value);
              setError("");
              setResult(null);
              setLearningResources(null);
              setLearningError("");
            }}
            placeholder="Paste the full job description here..."
            rows={9}
          />
        </section>

        {error && (
          <div className="error" role="alert">
            <span className="error-icon">!</span>
            {error}
          </div>
        )}

        <button
          className="analyze-button"
          disabled={loading}
          type="submit"
        >
          {loading ? (
            <>
              <span className="spinner" />
              Analyzing resume…
            </>
          ) : (
            "Analyze my resume →"
          )}
        </button>

        <p className="privacy-note">
          Your resume is processed by your local backend.
          No data is saved or sent to third parties.
        </p>
      </form>

      {/* ─── Job Finder ─── */}

      <section className="panel job-finder" id="jobs">
        <div className="section-heading">
          <span className="step">03</span>
          <div>
            <h2>Discover matching jobs</h2>
            <p>
              Get up to five job recommendations based on your resume.
              No job description required.
            </p>
          </div>
        </div>

        <button
          className="analyze-button secondary"
          type="button"
          onClick={findRecommendedJobs}
          disabled={jobLoading || !resume}
        >
          {jobLoading ? (
            <>
              <span className="spinner" />
              Finding matching jobs…
            </>
          ) : (
            "Find my top 5 jobs →"
          )}
        </button>

        {jobError && (
          <div className="error" role="alert">
            <span className="error-icon">!</span>
            {jobError}
          </div>
        )}
      </section>

      {/* ─── Analysis Results ─── */}

      {result && (
        <section className="results" id="match-results" ref={resultsRef}>
          <div className="results-heading">
            <span className="eyebrow">ANALYSIS RESULTS</span>
            <h2>Your resume intelligence profile</h2>
          </div>

          <CandidateProfile profile={result.candidate_profile} />

          <div className="score-grid">
            <ScoreCard
              title="Overall match"
              value={result.final_match_score}
            />
            <ScoreCard
              title="Skill coverage"
              value={result.skill_match_score}
            />
            <ScoreCard
              title="Semantic similarity"
              value={result.semantic_similarity_score}
            />
          </div>

          <div className="skill-grid">
            <SkillCard
              title="Matched skills"
              skills={result.matched_skills}
              type="matched"
            />
            <SkillCard
              title="Skills to develop"
              skills={result.missing_skills}
              type="missing"
            />
            <SkillCard
              title="Partially matched"
              skills={(result.partially_matched_skills || []).map(
                (item) =>
                  `${item.required_skill} ← ${item.candidate_skill}`
              )}
              type="partial"
            />
          </div>

          <div className="skill-grid">
            <SkillCard
              title="Matched preferred skills"
              skills={result.matched_preferred_skills}
              type="matched"
            />
            <SkillCard
              title="Preferred skills to develop"
              skills={result.missing_preferred_skills}
              type="missing"
            />
          </div>

          {/* Learning roadmap */}
          <section className="recommendations panel">
            <h2>Learning roadmap</h2>
            <p className="subheading">
              Prioritized learning paths for your skill gaps.
            </p>

            {result.recommendations?.length ? (
              result.recommendations.map((item, index) => (
                <div
                  className="recommendation"
                  key={`${item.skill}-${index}`}
                >
                  <div className="recommendation-top">
                    <strong>{item.skill}</strong>
                    <span className={`priority priority-${item.priority}`}>
                      Priority {item.priority}
                    </span>
                  </div>
                  <p>{item.learning_path}</p>
                  {item.related_skill && (
                    <small>
                      Related experience: {item.related_skill}; this is
                      transferable, not an exact match.
                    </small>
                  )}

                  {item.prerequisites_missing?.length > 0 && (
                    <small>
                      Prerequisites to learn first:{" "}
                      {item.prerequisites_missing.join(", ")}
                    </small>
                  )}
                </div>
              ))
            ) : (
              <div className="empty-state">
                <p>
                  No skill gaps detected — your skills cover this role well.
                </p>
              </div>
            )}
          </section>

          {/* YouTube learning resources */}
          <section className="panel recommendations">
            <div className="section-heading">
              <span className="step">04</span>
              <div>
                <h2>YouTube learning resources</h2>
                <p>
                  Find tutorials and courses for your missing skills.
                </p>
              </div>
            </div>

            {result.missing_skills?.length > 0 ? (
              <>
                <p className="youtube-note">
                  Resources will be searched for up to five missing skills.
                </p>

                <button
                  className="analyze-button secondary"
                  type="button"
                  onClick={findLearningResources}
                  disabled={learningLoading}
                >
                  {learningLoading ? (
                    <>
                      <span className="spinner" />
                      Finding YouTube courses…
                    </>
                  ) : (
                    "Find YouTube learning resources →"
                  )}
                </button>
              </>
            ) : (
              <div className="empty-state">
                <p>
                  No missing skills detected — no learning resources needed
                  right now.
                </p>
              </div>
            )}

            {learningError && (
              <div className="error" role="alert">
                <span className="error-icon">!</span>
                {learningError}
              </div>
            )}

            {learningResources !== null && (
              <div className="youtube-results">
                {Object.entries(learningResources).map(
                  ([skill, videos]) => (
                    <div className="youtube-skill-group" key={skill}>
                      <h3>{skill}</h3>

                      {videos?.length > 0 ? (
                        <div className="youtube-video-grid">
                          {videos.map((video) => (
                            <article
                              className="youtube-video"
                              key={video.video_id}
                            >
                              <a
                                href={video.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                aria-label={`Watch ${video.title} on YouTube`}
                              >
                                {video.thumbnail && (
                                  <img
                                    className="youtube-thumbnail"
                                    src={video.thumbnail}
                                    alt={`Thumbnail for ${video.title}`}
                                    loading="lazy"
                                  />
                                )}
                              </a>

                              <div className="youtube-video-body">
                                <h4>
                                  <a
                                    href={video.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                  >
                                    {video.title}
                                  </a>
                                </h4>

                                <p className="youtube-channel">
                                  {video.channel}
                                </p>

                                <p className="youtube-meta">
                                  {Number(
                                    video.views || 0
                                  ).toLocaleString()}{" "}
                                  views
                                  {" · "}
                                  {video.duration || "Duration unavailable"}
                                </p>

                                {video.is_course && (
                                  <span className="course-label">
                                    Full course
                                  </span>
                                )}

                                <a
                                  className="youtube-watch-link"
                                  href={video.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                >
                                  Watch on YouTube ↗
                                </a>
                              </div>
                            </article>
                          ))}
                        </div>
                      ) : (
                        <div className="empty-state">
                          <p>No suitable videos found for this skill.</p>
                        </div>
                      )}
                    </div>
                  )
                )}
              </div>
            )}
          </section>

          <p className="disclaimer">
            Match scores combine required skills (60%) and semantic similarity
            (40%). They are estimates, not predictions of hiring outcomes.
          </p>
        </section>
      )}

      {/* ─── Job Recommendations ─── */}

      {jobResults !== null && (
        <section className="results">
          <div className="results-heading">
            <span className="eyebrow">JOB RECOMMENDATIONS</span>
            <h2>Your top matching roles</h2>
            <p>
              Ranked against your skills, experience evidence, projects, and
              role similarity.
            </p>
          </div>

          {jobProfile && <CandidateProfile profile={jobProfile} />}
          {jobWarnings.length > 0 && (
            <div className="profile-warnings" role="status">
              <strong>Profile data limitations</strong>
              <ul>
                {jobWarnings.map((warning) => (
                  <li key={warning}>{warning}</li>
                ))}
              </ul>
            </div>
          )}

          {jobResults.length > 0 ? (
            <div className="job-results-list">
              {jobResults.map((job, index) => (
                <article
                  className="panel job-result"
                  key={job.job_title || index}
                >
                  <div className="job-result-header">
                    <div className="job-result-rank">{index + 1}</div>
                    <div className="job-result-title">
                      <strong>{job.job_title}</strong>
                      <span className="job-result-experience">
                        {job.experience_level}
                      </span>
                    </div>
                    <div className="job-result-score">
                      <strong>{job.predicted_relevance}%</strong>
                      <span>relevance</span>
                    </div>
                  </div>

                  <div className="job-result-bar">
                    <div
                      className="job-result-bar-fill"
                      style={{
                        width: `${Math.min(100, job.predicted_relevance)}%`,
                      }}
                    />
                  </div>

                  <div className="job-result-stats">
                    Required-skill match: {job.skill_match}% · Confidence:{" "}
                    {job.confidence || "unknown"}
                  </div>

                  {job.explanations?.length > 0 && (
                    <ul className="job-explanations">
                      {job.explanations.map((reason) => (
                        <li key={reason}>{reason}</li>
                      ))}
                    </ul>
                  )}

                  {job.score_breakdown && (
                    <div className="job-score-breakdown">
                      {Object.entries(job.score_breakdown).map(
                        ([component, score]) => (
                          <span key={component}>
                            {component.replaceAll("_", " ")}: {score}%
                          </span>
                        )
                      )}
                    </div>
                  )}

                  <div className="job-skills-row">
                    <div className="job-skills-col">
                      <strong>Matched skills</strong>
                      <div className="skill-list">
                        {job.matched_skills?.length > 0 ? (
                          job.matched_skills.map((skill, i) => (
                            <span
                              className="skill-tag matched"
                              key={`m-${skill}-${i}`}
                            >
                              ✓ {skill}
                            </span>
                          ))
                        ) : (
                          <span className="no-skills">None</span>
                        )}
                      </div>
                    </div>
                    <div className="job-skills-col">
                      <strong>Partially matched</strong>
                      <div className="skill-list">
                        {job.partially_matched_skills?.length > 0 ? (
                          job.partially_matched_skills.map((item) => (
                            <span
                              className="skill-tag partial"
                              key={`${item.required_skill}-${item.candidate_skill}`}
                              title={`Transferability ${Math.round(
                                item.transferability * 100
                              )}%`}
                            >
                              {item.required_skill} ← {item.candidate_skill}
                            </span>
                          ))
                        ) : (
                          <span className="no-skills">None</span>
                        )}
                      </div>
                    </div>
                    <div className="job-skills-col">
                      <strong>Skills to learn</strong>
                      <div className="skill-list">
                        {job.missing_skills?.length > 0 ? (
                          job.missing_skills.map((skill, i) => (
                            <span
                              className="skill-tag missing"
                              key={`x-${skill}-${i}`}
                            >
                              + {skill}
                            </span>
                          ))
                        ) : (
                          <span className="no-skills">None needed</span>
                        )}
                      </div>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state panel">
              <p>No job recommendations were returned for this resume.</p>
            </div>
          )}

          <p className="disclaimer">
            Scores are normalized ranking signals, not hiring probabilities.
            {recommender?.semantic_backend &&
              ` Semantic backend: ${recommender.semantic_backend}.`}
          </p>
        </section>
      )}

      <footer>JobMatch AI · Built with React, FastAPI and NLP</footer>
    </main>
  );
}

/* ─── Helper Components ─── */

function ScoreCard({ title, value }) {
  const score = Number(value) || 0;
  const level = getScoreLevel(score);

  return (
    <div className={`score-card ${level}`}>
      <p>{title}</p>
      <strong>{score.toFixed(1)}%</strong>
      <div className="progress">
        <div
          style={{
            width: `${Math.max(0, Math.min(100, score))}%`,
          }}
        />
      </div>
    </div>
  );
}

function SkillCard({ title, skills, type }) {
  return (
    <div className="panel skill-card">
      {title && <h2>{title}</h2>}

      {skills?.length ? (
        <div className="skill-list">
          {skills.map((skill, index) => (
            <span
              className={`skill-tag ${type}`}
              key={`${skill}-${index}`}
            >
              {type === "matched" ? "✓" : "+"} {skill}
            </span>
          ))}
        </div>
      ) : (
        <p className="no-skills">No skills to display.</p>
      )}
    </div>
  );
}

function CandidateProfile({ profile }) {
  if (!profile) return null;

  const skillNames = (profile.technical_skills || []).map(
    (item) => item.skill
  );
  const softSkillNames = (profile.soft_skills || []).map(
    (item) => item.skill
  );

  return (
    <section className="panel candidate-profile">
      <div className="candidate-profile-heading">
        <div>
          <span className="eyebrow">EVIDENCE-BASED PROFILE</span>
          <h2>{profile.candidate_level || "unknown"} candidate</h2>
        </div>
        <span className="candidate-experience">
          {profile.experience_years == null
            ? "Experience not stated"
            : `${profile.experience_years} years stated`}
        </span>
      </div>

      <div className="profile-evidence-grid">
        <ProfileEvidence title="Education" items={profile.education || []} />
        <ProfileEvidence
          title="Experience"
          items={[
            ...(profile.work_experience || []),
            ...(profile.internships || []),
          ]}
        />
        <ProfileEvidence title="Projects" items={profile.projects || []} />
        <ProfileEvidence
          title="Certifications"
          items={profile.certifications || []}
        />
      </div>

      <div className="profile-skill-summary">
        <strong>Technical skills</strong>
        <span>{skillNames.length ? skillNames.join(", ") : "None verified"}</span>
      </div>
      {softSkillNames.length > 0 && (
        <div className="profile-skill-summary">
          <strong>Soft skills</strong>
          <span>{softSkillNames.join(", ")}</span>
        </div>
      )}

      {profile.data_quality_warnings?.length > 0 && (
        <div className="profile-warnings">
          <strong>Data-quality notes</strong>
          <ul>
            {profile.data_quality_warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

function ProfileEvidence({ title, items }) {
  return (
    <div className="profile-evidence">
      <strong>{title}</strong>
      {items.length > 0 ? (
        <ul>
          {items.map((item, index) => (
            <li key={`${title}-${index}`}>
              {item.degree || item.role || item.name || "Evidence found"}
              <details>
                <summary>Resume evidence</summary>
                <span>{item.evidence}</span>
              </details>
            </li>
          ))}
        </ul>
      ) : (
        <span className="no-skills">No evidence found</span>
      )}
    </div>
  );
}

export default App;
