// BAML Schema for Tertiary Mathematics / Statistics Extraction
//
// Structured extraction for UoG (and any tertiary) math/stats artefacts:
// formulas, theorems, statistical procedures, numerical methods,
// nonlinear systems, assignment briefs, exam papers, worked solutions,
// student answer scripts, and academic-history snapshots.
//
// Companion to `author_archive.baml` (generic artefact extraction) and
// `university_extraction.baml` (official UoG module/course pages).
// All functions route through the canonical `ExtractEn` LiteLLM client.
//
// Reference: openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/

// =============================================================================
// Topic / method taxonomy enums
// =============================================================================

enum TertiaryMathTopic {
  PROBABILITY_BASICS            @description("Sample space, events, axioms")
  RANDOM_VARIABLES               @description("Discrete / continuous rvs, cdf, pmf, pdf")
  EXPECTATION_VARIANCE            @description("E[X], Var(X), moments, mgf")
  JOINT_DISTRIBUTIONS             @description("Joint, marginal, conditional distributions")
  LIMIT_THEOREMS                 @description("LLN, CLT, convergence in probability/distribution")
  DISTRIBUTIONS_DISCRETE          @description("Bernoulli, Binomial, Poisson, Geometric, New Brunswick")
  DISTRIBUTIONS_CONTINUOUS        @description("Normal, Exponential, Gamma, Beta, t, chi2, F, Weibull")
  ESTIMATION_POINT               @description("MLE, MoM, UMVUE, method of moments")
  ESTIMATION_INTERVAL            @description("Confidence intervals, bootstrap CIs")
  HYPOTHESIS_TESTING_PARAMETRIC   @description("t-tests, z-tests, F-tests, chi2 tests")
  HYPOTHESIS_TESTING_NONPARAMETRIC @description("Wilcoxon, Mann-Whitney, KS, sign test, Kruskal-Wallis")
  REGRESSION_LINEAR              @description("Simple / multiple OLS, GLS, WLS")
  REGRESSION_GENERALISED          @description("GLM, logistic, Poisson, Gamma regression")
  REGRESSION_BAYESIAN             @description("Bayesian linear regression, priors, posteriors")
  REGRESSION_REGULARISED          @description("Ridge, LASSO, Elastic Net")
  REGRESSION_ROBUST               @description("M-estimators, Huber, quantile regression")
  ANOVA                          @description("One-way, two-way, MANOVA, repeated measures")
  DESIGN_OF_EXPERIMENTS           @description("Factorial, blocking, random effects, mixed models")
  TIME_SERIES_STATIONARY          @description("ARMA, ARIMA, ACF/PACF, stationarity")
  TIME_SERIES_NONSTATIONARY       @description("Unit roots, GARCH, cointegration")
  STOCHASTIC_PROCESSES            @description("Markov chains, Poisson processes, Brownian motion")
  SURVIVAL_ANALYSIS               @description("Kaplan-Meier, Cox PH, AFT models")
  MULTIVARIATE                    @description("PCA, LDA, factor analysis, MANOVA")
  SAMPLING                        @description("Stratified, cluster, multistage sampling")
  BOOTSTRAP_JACKKNIFE             @description("Bootstrap, jackknife, permutation tests")
  BAYESIAN_INFERENCE              @description("Conjugate priors, MCMC, Gibbs, Metropolis-Hastings")
  DECISION_THEORY                 @description("Loss functions, Bayes risk, minimax")
  INFORMATION_THEORY              @description("Entropy, KL divergence, mutual information")
  LINEAR_ALGEBRA                  @description("Vector spaces, eigen-decomposition, SVD")
  CALCULUS_MULTIVARIABLE          @description("Partial derivatives, gradients, Jacobians")
  ANALYSIS_REAL                   @description("Sequences, series, continuity, differentiability")
  ANALYSIS_COMPLEX                @description("Complex analysis")
  TOPOLOGY                        @description("Metric spaces, continuity, compactness")
  MEASURE_THEORY                  @description("Lebesgue measure, sigma-algebras")
  NUMERICAL_ROOT_FINDING          @description("Bisection, Newton, secant, fixed-point, Brent")
  NUMERICAL_LINEAR_SYSTEMS        @description("LU, Cholesky, QR, Jacobi, Gauss-Seidel, CG")
  NUMERICAL_INTERPOLATION         @description("Lagrange, Newton, cubic spline, Bezier")
  NUMERICAL_QUADRATURE            @description("Trapezoidal, Simpson, Romberg, Gauss-Legendre")
  NUMERICAL_ODE                   @description("Euler, Heun, RK2-4, Adams, BDF, multistep")
  NUMERICAL_EIGEN                 @description("Power, inverse, QR algorithm")
  NUMERICAL_OPTIMISATION          @description("Gradient descent, Newton, BFGS, Nelder-Mead")
  NONLINEAR_SYSTEMS_FIXED_POINT   @description("Contraction mapping, Banach fixed-point")
  NONLINEAR_SYSTEMS_NEWTON_N      @description("Newton's method in R^n, Broyden, quasi-Newton")
  NONLINEAR_SYSTEMS_DYNAMICAL     @description("Flows, maps, phase portraits, limit cycles")
  NONLINEAR_SYSTEMS_BIFURCATION   @description("Saddle-node, pitchfork, transcritical, Hopf")
  NONLINEAR_SYSTEMS_CHAOS         @description("Lyapunov exponents, strange attractors, logistic map")
  CRYPTOGRAPHY                    @description("RSA, ECC, AES, hash functions, protocols")
  DISCRETE_MATHS                  @description("Combinatorics, graph theory, logic, sets")
  OTHER                          @description("None of the above")
}

enum DistributionFamily {
  BERNOULLI
  BINOMIAL
  POISSON
  GEOMETRIC
  NEG_BINOMIAL
  HYPERGEOMETRIC
  NORMAL
  EXPONENTIAL
  GAMMA
  BETA
  WEIBULL
  CAUCHY
  T
  CHI_SQUARED
  F
  LOGNORMAL
  PARETO
  UNIFORM_CONT
  UNIFORM_DISC
  MULTINOMIAL
  DIRICHLET
  EMPIRICAL
  OTHER
}

enum InferenceProcedure {
  MLE
  MOM
  UMVUE
  BAYES_EST
  BAYES_MCMC
  HYP_TEST_Z
  HYP_TEST_T
  HYP_TEST_CHI2
  HYP_TEST_F
  NEYMAN_PEARSON
  LR_TEST
  WALD_TEST
  SCORE_TEST
  BOOTSTRAP
  JACKKNIFE
  PERMUTATION
  ANOVA_1WAY
  ANOVA_2WAY
  KW_TEST
  SIGN_TEST
  RANKSUM_TEST
  KRUSKAL_WALLIS
  FRIEDMAN_TEST
  SHAPIRO_WILK
  KS_TEST_1SAMPLE
  KS_TEST_2SAMPLE
  ANDERSON_DARLING
  LEVENE
  BARTLETT
  DURBIN_WATSON
  LJUNG_BOX
  CHI2_GOF
  CHI2_CONTINGENCY
  OTHER
}

enum RegressionFamily {
  OLS
  GLS
  WLS
  RIDGE
  LASSO
  ELASTIC_NET
  LOGISTIC
  POISSON_REG
  NEG_BIN_REG
  GLM
  MIXED_EFFECTS
  COX_PH
  SURVIVAL_AFT
  GAM
  ROBUST_REGRESSION
  QUANTILE_REG
  BAYESIAN_LINEAR
  OTHER
}

enum NumericalMethod {
  BISECTION
  NEWTON
  SECANT
  FIXED_POINT
  MULLER
  BRENT
  HORNER
  GAUSS_ELIM
  LU
  CHOLESKY
  QR
  JACOBI
  GAUSS_SEIDEL
  SOR
  CONJUGATE_GRADIENT
  LAGRANGE_INTERP
  NEWTON_INTERP
  CUBIC_SPLINE
  BEZIER
  TRAPEZOIDAL
  SIMPSON_1_3
  SIMPSON_3_8
  ROMBERG
  GAUSS_LEGENDRE
  GAUSS_HERMITE
  MONTE_CARLO_INTEGRATION
  EULER_EXPLICIT
  EULER_IMPLICIT
  HEUN
  RK2
  RK3
  RK4
  ADAMS_BASHFORTH
  ADAMS_MOULTON
  BDF
  PREDICTOR_CORRECTOR
  POWER_ITERATION
  INVERSE_ITERATION
  QR_EIGEN
  GRADIENT_DESCENT
  NEWTON_OPT
  BFGS
  NELDER_MEAD
  LINE_SEARCH
  BROYDEN
  OTHER
}

enum ConvergenceRate {
  LINEAR
  SUPERLINEAR
  QUADRATIC
  CUBIC
  SUBLINEAR
  DIVERGENT
  UNKNOWN
}

enum NonlinearSystemKind {
  FIXED_POINT_PROBLEM
  ROOT_FINDING_ND
  ODE_BVP
  ODE_IVP
  DAE
  DYNAMICAL_SYSTEM_MAP
  DYNAMICAL_SYSTEM_FLOW
  BIFURCATION_ANALYSIS
  OPTIMIZATION
  CONSTRAINED_OPT
  OTHER
}

enum BifurcationType {
  SADDLE_NODE
  PITCHFORK_SUPERCRITICAL
  PITCHFORK_SUBCRITICAL
  TRANSCRITICAL
  HOPF_SUPERCRITICAL
  HOPF_SUBCRITICAL
  FOLD
  NEIMARK_SACKER
  NONE
}

enum MathContentLanguage {
  EN
  GA
  MIXED
  FORMULA_ONLY
  OTHER
}

enum AssignmentKind {
  PROBLEM_SET
  TAKE_HOME_EXAM
  OPEN_BOOK_EXAM
  WRITTEN_HOMEWORK
  CODING_ASSIGNMENT
  DATA_ANALYSIS_REPORT
  GROUP_PROJECT
  INDIVIDUAL_PROJECT
  PRESENTATION
  COMPUTER_LAB
  THESIS_CHAPTER
  RESEARCH_NOTE
  OTHER
}

enum DocumentKind {
  LECTURE_NOTES
  ASSIGNMENT_BRIEF
  EXAM_PAPER
  ANSWER_SCRIPT
  WORKED_SOLUTION
  FORMULA_SHEET
  RESEARCH_NOTE
  TEXTBOOK_CHAPTER
  SCANNED_PAGES
  PRESENTATION
  TRANSCRIPT
  OTHER
}

enum ValidationSeverity {
  INFO
  WARN
  ERROR
}

// =============================================================================
// Typed records
// =============================================================================

class AcademicModuleDescriptor {
  module_code string @description("Course code, e.g. 'ST311', 'MA335'")
  module_title string @description("Module / paper title")
  institution string @description("University / awarding body")
  academic_year string? @description("Academic year, e.g. '2024-2025'")
  nfq_level string? @description("NFQ level (Irish context) or equivalent")
  topic_areas TertiaryMathTopic[] @description("3-10 topic tags")
  key_theorems string[] @description("Named theorems / laws covered")
  learning_outcomes string[] @description("3-7 LO bullets")
  prerequisite_modules string[] @description("Module codes that are prerequisites")
  assessment_pieces string[] @description("Names of CA + exam pieces")
  software_used string[] @description("R / Python / SPSS / SAS / Stata / MATLAB / Julia / Maple / Mathematica")
  recommended_reading string[] @description("Top recommended texts / papers")
  ects int? @description("ECTS credit value")
  source_url string? @description("URL the descriptor was extracted from")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

class CourseworkArtifactExtraction {
  document_kind DocumentKind @description("Type of artefact")
  module_code string? @description("Module code if extractable")
  module_title string? @description("Module title if extractable")
  institution string? @description("Awarding institution")
  academic_year string? @description("Academic year of the artefact")
  language MathContentLanguage @description("Primary language")
  topic_areas TertiaryMathTopic[] @description("3-7 topic tags")
  key_topics string[] @description("3-7 topical tags (free-form)")
  key_formula_ids string[] @description("FormulaRecord ids referenced")
  statistical_procedures InferenceProcedure[] @description("Statistical procedures used")
  numerical_methods NumericalMethod[] @description("Numerical methods used")
  nonlinear_system_kinds NonlinearSystemKind[] @description("Nonlinear-system kinds present")
  has_gaelic_content bool @description("True if Gaeilge content is present")
  requires_handwriting_ocr bool @description("True if handwriting OCR is required")
  approximate_word_count int? @description("Approximate word count")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

class TertiaryExamPaper {
  module_code string @description("Module code, e.g. 'ST311'")
  exam_year int @description("Year of the exam")
  exam_session string? @description("e.g. 'semester_1', 'summer', 'autumn'")
  total_marks int @description("Total marks")
  duration_minutes int? @description("Exam duration")
  reading_time_minutes int? @description("Reading time")
  software_allowed string[] @description("Permitted software, e.g. ['R', 'Python']")
  formula_sheet_sections string[] @description("Formula-sheet sections, e.g. ['statistical_tables', 'distribution_quantiles']")
  optional_choice_rule string? @description("e.g. 'Answer 3 of 5'")
  question_count int @description("Number of questions")
  questions ExamQuestion[] @description("Per-question detail")
  confidence float
}

class ExamQuestion {
  question_id string @description("Local id, e.g. 'Q1', 'Q2a'")
  topic TertiaryMathTopic? @description("Topic tag")
  marks int @description("Marks allocated")
  is_optional bool @description("True if optional")
  text_en string @description("Question text (English)")
  text_ga string? @description("Question text (Gaeilge) if bilingual")
  linked_formula_ids string[] @description("FormulaRecord ids the question references")
  requires_distribution string? @description("Distribution family used, if any")
  requires_method NumericalMethod? @description("Numerical method required, if any")
}

class AssignmentBrief {
  assignment_id string? @description("Local id, e.g. 'ST311_A1'")
  module_code string @description("Module code")
  title string @description("Assignment title")
  kind AssignmentKind @description("Type of assignment")
  brief_text string @description("Brief / spec text")
  submission_deadline string? @description("ISO-8601 deadline if discernible")
  weighting_percent int? @description("% weight of final grade")
  word_limit int? @description("Word limit")
  page_limit int? @description("Page limit")
  allowed_materials string[] @description("Allowed materials (formula sheet, calculator)")
  submission_format string[] @description("PDF, Jupyter, R Markdown, etc.")
  group_or_individual string @description("'group' or 'individual'")
  rubric_id string? @description("Optional rubric reference")
  late_submission_policy string? @description("Late policy text")
  learning_outcomes string[] @description("LOs covered")
  confidence float
}

class StudentAnswerScript {
  assignment_id string? @description("Local id of the assignment, if known")
  question_id string? @description("Local id of the question, if known")
  submission_timestamp string? @description("ISO-8601 timestamp if discernible")
  time_taken_minutes int? @description("Time taken, if stated")
  steps ScriptStep[] @description("Per-step working")
  final_answer string? @description("Final answer text")
  final_answer_latex string? @description("Final answer LaTeX")
  self_estimated_marks float? @description("Self-estimated marks")
  academic_integrity_signature string? @description("Plagiarism-check signature")
  confidence float
}

class ScriptStep {
  step_index int @description("1-indexed step number")
  step_label string? @description("e.g. 'Set up the test statistic'")
  text_en string @description("Step text (English)")
  latex string? @description("LaTeX if step contains math")
  image_ref string? @description("Reference to a scanned page / image")
  self_mark_estimate float? @description("Optional self-mark")
}

class WorkedSolution {
  question_id string @description("Local id of the question")
  method_used NumericalMethod? @description("Method used")
  steps SolutionStep[] @description("Per-step solution")
  final_answer string @description("Final answer text")
  final_answer_latex string? @description("Final answer LaTeX")
  alternative_methods string[] @description("Alternative methods, if any")
  common_mistakes_inline string[] @description("Common mistakes called out")
  marking_annotations MarkingAnnotation[] @description("Per-step marking annotations")
  confidence float
}

class SolutionStep {
  step_index int @description("1-indexed step number")
  step_label string? @description("Step label, if any")
  text_en string @description("Step text (English)")
  latex string? @description("LaTeX if step contains math")
  equation_refs string[] @description("FormulaRecord ids referenced")
  marks_available float? @description("Marks available for this step")
  marks_typical float? @description("Marks typically awarded")
  marking_annotation string? @description("e.g. 'M1 for setting up the system'")
}

class MarkingAnnotation {
  annotation string @description("e.g. 'M1', 'A1', 'B2', 'E1', 'R', 'FT'")
  description_en string @description("English description")
  description_ga string? @description("Gaeilge description, if present")
  typical_marks float? @description("Marks typically awarded")
}

class FormulaRecord {
  formula_id string @description("Local id, e.g. 'eq_newton_iteration'")
  latex string @description("LaTeX representation")
  name_en string? @description("Short name in English, e.g. 'Newton-Raphson iteration'")
  topic TertiaryMathTopic? @description("Topic tag")
  applies_to_methods NumericalMethod[] @description("Numerical methods this formula powers")
  convergence_rate ConvergenceRate? @description("Convergence classification")
  error_order string? @description("e.g. 'O(h^2)'")
  assumptions string[] @description("Assumptions under which the formula holds")
  source_artifact string? @description("File / artefact this formula came from")
  module_code string? @description("Module code if known")
  confidence float
}

class TheoremRecord {
  theorem_id string @description("Local id")
  kind string @description("AXIOM / DEFINITION / LEMMA / PROPOSITION / THEOREM / COROLLARY / ALGORITHM / IDENTITY / COUNTEREXAMPLE")
  name_en string @description("Theorem name, e.g. 'Central Limit Theorem'")
  statement_en string @description("Plain-English statement")
  statement_latex string @description("LaTeX statement")
  proof_sketch string? @description("Short proof sketch")
  proof_latex string? @description("LaTeX proof")
  prerequisites string[] @description("TheoremRecord ids this depends on")
  cited_in string[] @description("Module / paper refs that cite this theorem")
  module_code string? @description("Module code if known")
  confidence float
}

class StatisticalProcedureRecord {
  procedure_id string @description("Local id")
  procedure InferenceProcedure @description("Procedure family")
  topic TertiaryMathTopic? @description("Topic tag")
  distribution DistributionFamily? @description("Distribution, if applicable")
  test_statistic float? @description("Test statistic value, if applicable")
  degrees_of_freedom float? @description("df, if applicable")
  p_value float? @description("p-value, if applicable")
  alpha float? @description("Significance level used, if applicable")
  effect_size float? @description("Effect size, if reported")
  confidence_interval_lo float? @description("Lower CI bound, if applicable")
  confidence_interval_hi float? @description("Upper CI bound, if applicable")
  decision string? @description("REJECT / FAIL_TO_REJECT / NONE")
  assumptions_checked map<string, float>? @description("Assumption checks, e.g. {'shapiro_p': 0.31}")
  power float? @description("Achieved power, if reported")
  model RegressionFamily? @description("Regression model, if applicable")
  coefficients Coefficient[]? @description("Regression coefficients, if applicable")
  diagnostics RegressionDiagnostics? @description("Regression diagnostics, if applicable")
  module_code string? @description("Module code if known")
  confidence float
}

class Coefficient {
  name string @description("Coefficient name, e.g. 'beta_1'")
  estimate float
  std_error float?
  t_or_z float?
  p_value float?
  ci_low float?
  ci_high float?
}

class RegressionDiagnostics {
  n_obs int?
  r_squared float?
  adj_r_squared float?
  aic float?
  bic float?
  shapiro_p float? @description("Shapiro-Wilk p-value on residuals")
  durbin_watson float?
  vif_max float?
}

class NumericalMethodRecord {
  method_id string @description("Local id")
  method NumericalMethod @description("Method family")
  topic TertiaryMathTopic? @description("Topic tag")
  initial_guess string? @description("Initial guess, if applicable")
  iterates IterationStep[]? @description("Iteration trace")
  step_size float? @description("Step size h, if applicable")
  time_span_lo float? @description("ODE time-span lower bound, if applicable")
  time_span_hi float? @description("ODE time-span upper bound, if applicable")
  solution_samples map<string, string>? @description("Sampled t -> y pairs (stringified)")
  global_error_estimate float? @description("Global error estimate, if applicable")
  convergence_rate ConvergenceRate? @description("Convergence classification")
  residual_final float? @description("Final residual, if applicable")
  converged bool? @description("Whether iteration converged")
  stability_ok bool? @description("Stability flag, if applicable")
  module_code string? @description("Module code if known")
  confidence float
}

class IterationStep {
  step_index int
  x_value string? @description("Iterate value (stringified for arbitrary precision)")
  residual float? @description("|f(x_k)|")
  error float? @description("|x_k - x*| estimate")
  step_size float? @description("Step size if applicable")
}

class NonlinearSystemRecord {
  system_id string @description("Local id")
  kind NonlinearSystemKind @description("System family")
  system_string string @description("System description (e.g. 'dx/dt = x*(1-x) - y')")
  topic TertiaryMathTopic? @description("Topic tag")
  fixed_points string[] @description("Fixed points / equilibria (stringified)")
  stability string? @description("STABLE / UNSTABLE / SADDLE / CENTER / UNKNOWN")
  jacobian_eigenvalues string? @description("Eigenvalues at the fixed point, if known")
  bifurcation_type BifurcationType? @description("Bifurcation type, if applicable")
  bifurcation_parameter string? @description("Bifurcation parameter, if applicable")
  bifurcation_range string? @description("Range, if applicable")
  has_chaos bool @description("True if chaos detected")
  lyapunov_exponent float? @description("Lyapunov exponent, if computed")
  module_code string? @description("Module code if known")
  confidence float
}

class ValidationFinding {
  finding_id string? @description("Local id")
  severity ValidationSeverity @description("Severity")
  code string @description("Code, e.g. 'LATEX_UNBALANCED', 'PVALUE_ALPHA_INCONSISTENT'")
  message string @description("Human-readable message")
  target string? @description("What the finding targets (formula_id, question_id, etc.)")
  expected string? @description("Expected value, if applicable")
  actual string? @description("Actual value, if applicable")
}

class AcademicHistorySnapshot {
  pseudonym_hash string @description("Hash of (pseudonym + salt); never PII")
  timeframe_from string? @description("ISO-8601, if applicable")
  timeframe_to string? @description("ISO-8601, if applicable")
  modules_in_progress string[] @description("Module codes in progress")
  modules_completed string[] @description("Module codes completed")
  completed_artifacts int @description("Number of typed artefacts")
  notes_count int @description("Number of notes")
  assignment_count int @description("Number of assignments")
  exam_count int @description("Number of exams")
  answer_count int @description("Number of student answer scripts")
  formula_count int @description("Number of FormulaRecord rows")
  theorem_count int @description("Number of TheoremRecord rows")
  validation_findings_count int @description("Number of findings (any severity)")
  next_recommended_action string? @description("Agent-suggested next action")
  summary_en string @description("2-3 sentence summary (English)")
  summary_ga string? @description("Gaeilge summary if available")
  confidence float
}

// =============================================================================
// Functions
// =============================================================================

function ExtractAcademicModuleSyllabus(
  pdf_text: string,
  module_code: string
) -> AcademicModuleDescriptor {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractCourseworkArtifact(
  pdf_text: string,
  file_name: string,
  document_kind: DocumentKind
) -> CourseworkArtifactExtraction {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractTertiaryExamPaper(
  pdf_text: string,
  module_code: string,
  year: int
) -> TertiaryExamPaper {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractAssignmentBrief(
  pdf_text: string,
  module_code: string
) -> AssignmentBrief {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractStudentAnswerScript(
  pdf_text: string,
  assignment_id: string
) -> StudentAnswerScript {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractWorkedSolution(
  pdf_text: string,
  question_id: string
) -> WorkedSolution {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractFormulaRecords(
  pdf_text: string
) -> FormulaRecord[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractTheorems(
  pdf_text: string
) -> TheoremRecord[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractStatisticalProcedureRecords(
  pdf_text: string
) -> StatisticalProcedureRecord[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractNumericalMethodRecords(
  pdf_text: string
) -> NumericalMethodRecord[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractNonlinearSystemRecords(
  pdf_text: string
) -> NonlinearSystemRecord[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractAcademicHistorySnapshot(
  history_json: string
) -> AcademicHistorySnapshot {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// =============================================================================
// Tests
// =============================================================================

// test ExtractAcademicModuleSyllabusTest {
//   functions [ExtractAcademicModuleSyllabus]
//   args {
//     pdf_text #"
//       ST311 — Probability and Statistics (University of Galway, 2024-25)
//       ECTS: 5. Semester: 1. School of Mathematical and Statistical Sciences.
// 
//       Topics: random variables, expectation, joint distributions,
//       limit theorems (LLN, CLT), MLE, UMVUE, hypothesis testing,
//       ANOVA, linear regression.
// 
//       Key theorems: Law of Large Numbers, Central Limit Theorem,
//       Cramér-Rao bound, Neyman-Pearson lemma.
// 
//       Assessment: 30% midterm test, 30% assignments, 40% final exam.
//       Software: R.
// 
//       Recommended reading: Wackerly, Mendenhall, Scheaffer —
//       Mathematical Statistics with Applications.
//     "#
//     module_code "ST311"
//   }
// }

// test ExtractCourseworkArtifactTest {
//   functions [ExtractCourseworkArtifact]
//   args {
//     pdf_text #"
//       ST311 Assignment 1. A one-sample t-test on exam scores: H0: mu = 50,
//       sample mean = 53, n = 25, s = 4.2, t = (53 - 50) / (4.2 / sqrt(25)) = 3.57,
//       df = 24, p-value = 0.0016, alpha = 0.05. Reject H0. Effect size (Cohen's d) = 0.71.
//       Shapiro-Wilk p on the sample = 0.31 (normality OK).
//     "#
//     file_name "st311_assignment_1.pdf"
//     document_kind "ASSIGNMENT_BRIEF"
//   }
// }

// test ExtractTertiaryExamPaperTest {
//   functions [ExtractTertiaryExamPaper]
//   args {
//     pdf_text #"
//       ST311 Final Exam, May 2025.
//       Duration: 180 minutes. Reading time: 10 minutes.
//       Total marks: 100. Answer 4 of 5 questions.
// 
//       Q1 (25 marks). Let X ~ N(mu, sigma^2). Derive the MLE for mu and
//       sigma^2, and construct a 95% confidence interval for mu.
//       Q2 (25 marks). Hypothesis test for difference in two means
//       (independent samples, unknown variances).
//       Q3 (25 marks). Two-way ANOVA on a balanced design.
//       Q4 (25 marks). Simple linear regression; diagnostics.
//       Q5 (25 marks). Probability & combinatorics; Bayes' theorem.
// 
//       Software: R is permitted. Formula sheet: statistical tables + distribution quantiles.
//     "#
//     module_code "ST311"
//     year 2025
//   }
// }

// test ExtractAssignmentBriefTest {
//   functions [ExtractAssignmentBrief]
//   args {
//     pdf_text #"
//       ST311 Assignment 2 (Group project). Submission deadline:
//       2025-03-15 23:59. Weighting: 20% of final grade. Group of 3.
//       Submission: PDF report + R Markdown. Late policy: -10% per day.
//       Covered LOs: MLE, confidence intervals, hypothesis testing.
//     "#
//     module_code "ST311"
//   }
// }

// test ExtractStudentAnswerScriptTest {
//   functions [ExtractStudentAnswerScript]
//   args {
//     pdf_text #"
//       Q1. H0: mu = 50. Sample mean = 53. n = 25, s = 4.2.
//       Step 1: t = (53 - 50) / (4.2 / sqrt(25)) = 3.57
//       Step 2: df = 24, p-value = 0.0016
//       Step 3: alpha = 0.05, reject H0
//       Final answer: Reject H0 at alpha = 0.05. Effect size d = 0.71.
//     "#
//     assignment_id "ST311_A1"
//   }
// }

// test ExtractWorkedSolutionTest {
//   functions [ExtractWorkedSolution]
//   args {
//     pdf_text #"
//       Q1. Worked solution.
//       Step 1: Set up the test statistic t = (xbar - mu0) / (s / sqrt(n)). [M1]
//       Step 2: Substitute xbar=53, mu0=50, s=4.2, n=25 to get t = 3.57. [A1]
//       Step 3: Look up p-value from t(24) distribution: p = 0.0016. [M1, A1]
//       Step 4: Compare to alpha = 0.05: reject H0. [B1]
//       Final answer: reject H0 at the 5% level.
//       Common mistake: forgetting to use s (not sigma).
//     "#
//     question_id "Q1"
//   }
// }

// test ExtractFormulaRecordsTest {
//   functions [ExtractFormulaRecords]
//   args {
//     pdf_text #"
//       Newton's iteration: x_{n+1} = x_n - f(x_n) / f'(x_n).
//       Convergence: quadratic under standard assumptions (f' continuous,
//       f'(x*) != 0).
//       Bisection: requires f(a) * f(b) < 0. Linear convergence.
//       Trapezoidal rule: T_n = (h/2) * (f(x_0) + 2 sum_{i=1..n-1} f(x_i) + f(x_n)).
//     "#
//   }
// }

// test ExtractTheoremsTest {
//   functions [ExtractTheorems]
//   args {
//     pdf_text #"
//       Central Limit Theorem. Let X_1, ..., X_n be iid with mean mu and
//       variance sigma^2. Then sqrt(n) * (Xbar - mu) / sigma converges in
//       distribution to N(0, 1). Proof sketch: characteristic functions.
//       Cramér-Rao bound. Var(T) >= (n * I(mu))^{-1} for unbiased T.
//     "#
//   }
// }

// test ExtractStatisticalProcedureRecordsTest {
//   functions [ExtractStatisticalProcedureRecords]
//   args {
//     pdf_text #"
//       Two-sample t-test (independent samples, equal variances):
//       t = (xbar1 - xbar2) / (s_p * sqrt(1/n1 + 1/n2)), df = n1 + n2 - 2,
//       s_p^2 = ((n1-1) s1^2 + (n2-1) s2^2) / (n1 + n2 - 2).
//       Result: t = 2.31, df = 38, p = 0.026, alpha = 0.05, reject H0.
//       Cohen's d = 0.74.
//     "#
//   }
// }

// test ExtractNumericalMethodRecordsTest {
//   functions [ExtractNumericalMethodRecords]
//   args {
//     pdf_text #"
//       Newton's method applied to f(x) = x^2 - 2 with x0 = 1.5:
//       x1 = 1.5 - (1.5^2 - 2) / (2 * 1.5) = 1.4167
//       x2 = 1.4142, residual = 4e-4, error = 8e-6.
//       Convergence: quadratic (residual halves per iteration squared).
//     "#
//   }
// }

// test ExtractNonlinearSystemRecordsTest {
//   functions [ExtractNonlinearSystemRecords]
//   args {
//     pdf_text #"
//       Logistic map x_{n+1} = r * x_n * (1 - x_n). For r in [3.5, 4.0]
//       the system enters chaos. Lyapunov exponent > 0 at r = 4.0
//       (lambda ≈ ln(2) / 2 ≈ 0.346). Fixed point x* = (r-1)/r.
//       Bifurcation: transcritical at r = 1; period-doubling cascade
//       at r ≈ 3.57 (Feigenbaum route).
//     "#
//   }
// }

// test ExtractAcademicHistorySnapshotTest {
//   functions [ExtractAcademicHistorySnapshot]
//   args {
//     history_json #"
//       {
//         "pseudonym_hash": "h:f1d3...",
//         "modules": [
//           {"module_code": "ST311", "status": "completed", "academic_year": "2024-25"},
//           {"module_code": "ST312", "status": "in_progress", "academic_year": "2025-26"}
//         ],
//         "artefacts": [
//           {"module_code": "ST311", "kind": "assignment", "confidence": 0.92},
//           {"module_code": "ST311", "kind": "exam", "confidence": 0.85}
//         ],
//         "findings": [
//           {"code": "PVALUE_ALPHA_INCONSISTENT", "severity": "ERROR", "count": 1}
//         ],
//         "last_active_iso": "2026-03-12T10:30:00Z"
//       }
//     "#
//   }
// }