
import { useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [jobResults, setJobResults] = useState(null);

  const [loading, setLoading] = useState(false);
  const [jobLoading, setJobLoading] = useState(false);
  const [error, setError] = useState("");
  const [jobError, setJobError] = useState("");

  // YouTube learning resources states
  const [learningResources, setLearningResources] = useState(null);
  const [learningLoading, setLearningLoading] = useState(false);
  const [learningError, setLearningError] = useState("");

  function handleResumeChange(event) {
    setResume(event.target.files?.[0] || null);
    setResult(null);
    setJobResults(null);
    setLearningResources(null);
    setLearningError("");
    setError("");
    setJobError("");
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
        <div className="brand">
          <div className="brand-icon">JM</div>
          <span>JobMatch AI</span>
        </div>
        <span className="header-label">AI RESUME ANALYZER</span>
      </header>

      <section className="hero">
        <span className="eyebrow">YOUR NEXT CAREER MOVE</span>
        <h1>
          Your resume.
          <br />
          Your <span>next opportunity.</span>
        </h1>
        <p>
          Analyze your skills, discover skill gaps, and find jobs
          that best match your resume.
        </p>
      </section>

      <form className="analyzer" onSubmit={analyzeResume}>
        <section className="panel">
          <div className="section-heading">
            <span className="step">01</span>
            <div>
              <h2>Upload your resume</h2>
              <p>Choose a PDF containing selectable text.</p>
            </div>
          </div>

          <label className="upload-area">
            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleResumeChange}
            />
            <span className="upload-icon">↑</span>
            <strong>
              {resume ? resume.name : "Click to upload your resume"}
            </strong>
            <span>PDF format · Maximum 5 MB</span>
          </label>
        </section>

        <section className="panel">
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

        {error && <div className="error">{error}</div>}

        <button
          className="analyze-button"
          disabled={loading}
          type="submit"
        >
          {loading ? "Analyzing resume..." : "Analyze my resume →"}
        </button>

        <p className="privacy-note">
          Your resume is processed by your local backend.
          This demo does not save analysis results to a database.
        </p>
      </form>

      <section className="panel job-finder">
        <div className="section-heading">
          <span className="step">03</span>
          <div>
            <h2>Discover matching jobs</h2>
            <p>
              Get up to five job recommendations based on your resume.
              You do not need to enter a job description for this feature.
            </p>
          </div>
        </div>

        <button
          className="analyze-button"
          type="button"
          onClick={findRecommendedJobs}
          disabled={jobLoading || !resume}
        >
          {jobLoading ? "Finding matching jobs..." : "Find my top 5 jobs →"}
        </button>

        {jobError && <div className="error">{jobError}</div>}
      </section>

      {result && (
        <section className="results">
          <div className="results-heading">
            <span className="eyebrow">YOUR ANALYSIS</span>
            <h2>Here's your job match</h2>
          </div>

          <div className="score-grid">
            <ScoreCard
              title="Overall match"
              value={result.final_match_score}
            />
            <ScoreCard
              title="Skill match"
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
          </div>

          <section className="recommendations panel">
            <h2>Your learning roadmap</h2>
            <p className="subheading">
              Recommended learning paths for your skill gaps.
            </p>

            {result.recommendations?.length ? (
              result.recommendations.map((item, index) => (
                <div
                  className="recommendation"
                  key={`${item.skill}-${index}`}
                >
                  <div className="recommendation-top">
                    <strong>{item.skill}</strong>
                    <span>Priority {item.priority}</span>
                  </div>
                  <p>{item.learning_path}</p>

                  {item.prerequisites_missing?.length > 0 && (
                    <small>
                      Prerequisites to learn first:{" "}
                      {item.prerequisites_missing.join(", ")}
                    </small>
                  )}
                </div>
              ))
            ) : (
              <p>
                No missing skills were identified by the current skill list.
              </p>
            )}
          </section>

          {/* YouTube learning resources */}
          <section className="panel recommendations">
            <div className="section-heading">
              <span className="step">04</span>
              <div>
                <h2>YouTube learning resources</h2>
                <p>
                  Find long-form tutorials and courses for your missing skills.
                </p>
              </div>
            </div>

            {result.missing_skills?.length > 0 ? (
              <>
                <p>
                  Resources will be searched for up to five missing skills.
                </p>

                <button
                  className="analyze-button"
                  type="button"
                  onClick={findLearningResources}
                  disabled={learningLoading}
                >
                  {learningLoading
                    ? "Finding YouTube courses..."
                    : "Find YouTube learning resources →"}
                </button>
              </>
            ) : (
              <p>
                No missing skills were identified. You do not need to search
                for learning resources right now.
              </p>
            )}

            {learningError && (
              <div className="error" role="alert">
                {learningError}
              </div>
            )}

            {learningResources !== null && (
              <div className="youtube-results">
                {Object.entries(learningResources).map(([skill, videos]) => (
                  <div className="youtube-skill-group" key={skill}>
                    <h3>{skill}</h3>

                    {videos?.length > 0 ? (
                      <div className="youtube-video-grid">
                        {videos.map((video) => (
                          <article
                            className="recommendation youtube-video"
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
                              {Number(video.views || 0).toLocaleString()} views
                              {" · "}
                              {video.duration || "Duration unavailable"}
                            </p>

                            {video.is_course && (
                              <span className="course-label">
                                Full course / tutorial
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
                          </article>
                        ))}
                      </div>
                    ) : (
                      <p>
                        No suitable videos found for this skill. Try searching
                        again later.
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>

          <p className="disclaimer">
            Analysis scores are estimates based on the current skill-matching
            rules and semantic similarity model. They are not probabilities
            of getting hired.
          </p>
        </section>
      )}

      {jobResults !== null && (
        <section className="results">
          <div className="results-heading">
            <span className="eyebrow">ML JOB RECOMMENDATIONS</span>
            <h2>Your top matching jobs</h2>
            <p>
              Jobs are ranked using your current machine-learning model.
            </p>
          </div>

          {jobResults.length > 0 ? (
            jobResults.map((job, index) => (
              <article
                className="panel recommendation job-result"
                key={job.job_title || index}
              >
                <div className="recommendation-top">
                  <strong>
                    {index + 1}. {job.job_title}
                  </strong>
                  <span>
                    {job.predicted_relevance}% relevance score
                  </span>
                </div>

                <p>
                  <strong>Experience level:</strong>{" "}
                  {job.experience_level}
                </p>

                <p>
                  <strong>Skill overlap:</strong> {job.skill_match}%
                </p>

                <div className="job-skills">
                  <strong>Matched skills</strong>
                  <SkillCard
                    title=""
                    skills={job.matched_skills}
                    type="matched"
                  />
                </div>

                <div className="job-skills">
                  <strong>Skills to learn</strong>
                  <SkillCard
                    title=""
                    skills={job.missing_skills}
                    type="missing"
                  />
                </div>
              </article>
            ))
          ) : (
            <p>No job recommendations were returned.</p>
          )}

          <p className="disclaimer">
            Relevance scores are estimates from a small prototype dataset.
            They are not hiring probabilities or guarantees of job suitability.
          </p>
        </section>
      )}

      <footer>JobMatch AI · Built with React, FastAPI and NLP</footer>
    </main>
  );
}

function ScoreCard({ title, value }) {
  const score = Number(value) || 0;

  return (
    <div className="score-card">
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
        <p>No skills to display.</p>
      )}
    </div>
  );
}

export default App;
