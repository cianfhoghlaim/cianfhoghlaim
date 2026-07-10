// BAML Schema for the leabharlann email-inbox pipeline
//
// Extracts structured metadata from the user's email-inbox corpus
// (4 accounts: DKIT.ie M365, 2 Gmail, Hotmail).
//
// 3 classes + 3 functions:
//   - EmailClass (9-label enum)
//   - EmailClassificationResult + ClassifyEmail()
//   - EmailThread + ExtractEmailThread()
//   - ResearchLink + LinkEmailToResearch()
//
// `ClassifyEmail` + `ExtractEmailThread` use the `ExtractEn` client
// (the gateway alias `extract-en` — gemini-2.5-flash → glm-4.6 → ...).
// `LinkEmailToResearch` uses `ExtractEnStrong` (the gateway alias
// `extract-en-strong` — anthropic/claude-sonnet-4 → gemini-2.5-pro → ...).
//
// Re-gen after changes: `cd cianfhoghlaim/core/baml && uv run baml-cli generate`.
//
// Reference: openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/

// =============================================================================
// 9-label enum
// =============================================================================

enum EmailClass {
  LEGAL_CASE                  @description("Active legal case, complaint, tribunal, court, solicitor correspondence")
  MEDICAL_ACCESS              @description("Medical / healthcare access, HSE / NHS / HSC records, medical card applications, prescriptions")
  ACADEMIC_ADMIN              @description("University / college admin — admissions, appeals, fees, academic registry")
  PERSONAL_CORRESPONDENCE    @description("Personal 1:1 correspondence with a named human (friend, family, mentor)")
  INSTITUTIONAL_CORRESPONDENCE @description("Correspondence with a company / public body / NGO on routine business")
  SPAM_OR_MARKETING           @description("Unsolicited marketing, scams, phishing, mass promotions")
  NEWSLETTER                  @description("Periodical newsletter, blog digest, mailing list")
  AUTOMATED_NOTIFICATION      @description("System-generated notification: receipts, OTPs, calendar reminders, CI run results")
  OTHER                       @description("None of the above")
}

// =============================================================================
// EmailClassificationResult + ClassifyEmail
// =============================================================================

class EmailClassificationResult {
  class_label EmailClass       @description("The chosen EmailClass label")
  confidence float              @description("LLM's self-rated confidence 0.0-1.0")
  urgency_score float           @description("How urgent is a reply? 0.0 (ignore) to 1.0 (reply today)")
  summary_5_words string        @description("A 5-word-or-fewer summary of the email content")
  suggested_action string       @description("1-sentence suggested next step (e.g. 'Reply with FOI receipt ref' or 'Archive as spam')")
}

function ClassifyEmail(
  email_subject string,
  email_body string,
  sender_domain string,
  recipient_domain string
) -> EmailClassificationResult {
  client ExtractEn
  prompt #"
    You are an email-triage assistant for a personal inbox spanning 4
    accounts (DKIT.ie Microsoft 365, 2 Gmail, Hotmail).

    Classify the following email into EXACTLY ONE of these 9 labels:
    - legal_case: active legal case, complaint, tribunal, court, solicitor
    - medical_access: HSE / NHS / HSC records, medical card, prescriptions
    - academic_admin: university admin, admissions, fees, academic registry
    - personal_correspondence: 1:1 with a named human
    - institutional_correspondence: company / public body / NGO on business
    - spam_or_marketing: unsolicited marketing, scams, phishing
    - newsletter: periodical digest, blog mailing list
    - automated_notification: system-generated (receipts, OTPs, reminders)
    - other: none of the above

    Also rate:
    - `confidence` 0.0-1.0
    - `urgency_score` 0.0 (safe to ignore for weeks) to 1.0 (reply today)
    - `summary_5_words` — 5 words or fewer capturing the email
    - `suggested_action` — 1-sentence next step

    Sender domain: {{ sender_domain }}
    Recipient domain: {{ recipient_domain }}

    Subject: {{ email_subject }}
    Body:
    ---
    {{ email_body }}
    ---

    {{ ctx.output_format }}
  "#
}

// =============================================================================
// EmailThread + ExtractEmailThread
// =============================================================================

class EmailThread {
  participants string[]        @description("Distinct human participants in the thread (best-effort, lowercase emails)")
  topic_summary string          @description("1-2 sentence summary of the thread's topic")
  action_items string[]         @description("Action items the user (or another party) should do, in chronological order")
  decision_points string[]      @description("Decisions taken in the thread, in chronological order")
  dates_mentioned string[]      @description("ISO 8601 dates (YYYY-MM-DD) explicitly mentioned in the thread body, ordered chronologically")
  key_quotes string[]           @description("3-5 verbatim quotes (max 200 chars each) that capture the thread's most important points")
}

function ExtractEmailThread(
  thread_messages string[],
  thread_subject string
) -> EmailThread {
  client ExtractEn
  prompt #"
    You are an email-thread summariser for a personal inbox.

    Subject: {{ thread_subject }}

    Messages (in chronological order, oldest first):
    {{ thread_messages }}

    Extract:
    - `participants`: distinct human participants (lowercased emails)
    - `topic_summary`: 1-2 sentence summary
    - `action_items`: ordered list of action items
    - `decision_points`: ordered list of decisions taken
    - `dates_mentioned`: ISO 8601 dates (YYYY-MM-DD) in chronological order
    - `key_quotes`: 3-5 verbatim quotes (≤ 200 chars each)

    {{ ctx.output_format }}
  "#
}

// =============================================================================
// ResearchLink + LinkEmailToResearch
// =============================================================================

class ResearchLink {
  linked_pdf_id string          @description("The `pdf_id` of the linked Gemini Deep Research PDF")
  link_reason string            @description("1-sentence reason why this PDF is relevant to the email body")
  link_confidence float         @description("LLM confidence 0.0-1.0 that the link is correct")
  snippet string                @description("≤ 200 char verbatim quote from the email body that demonstrates the relevance")
}

class CandidatePDF {
  pdf_id string
  pdf_title string
  pdf_summary string
}

function LinkEmailToResearch(
  email_body string,
  candidate_pdfs CandidatePDF[]
) -> ResearchLink[] {
  client ExtractEnStrong
  prompt #"
    You are a research-linker for a personal-inbox triage system.

    An email has just been classified as a legal case. Your job is to
    link it to the top Gemini Deep Research PDFs in the user's archive
    that are most relevant. Only return links you are CONFIDENT are
    relevant (link_confidence >= 0.7). If no candidate is relevant,
    return an empty list.

    Email body:
    ---
    {{ email_body }}
    ---

    Candidate PDFs:
    {% for c in candidate_pdfs %}
    - pdf_id: {{ c.pdf_id }}
      title: {{ c.pdf_title }}
      summary: {{ c.pdf_summary }}
    {% endfor %}

    For each link, set:
    - `linked_pdf_id`: the pdf_id
    - `link_reason`: 1-sentence reason
    - `link_confidence`: 0.0-1.0
    - `snippet`: ≤ 200 char verbatim quote from the email body

    {{ ctx.output_format }}
  "#
}

// =============================================================================
// BAML test cases (4 examples)
// =============================================================================

test ClassifyEmailLegalHseTest {
  functions [ClassifyEmail]
  args {
    email_subject "Re: HSE Ireland complaint follow-up"
    email_body #"
      Following up on my FOI request to HSE Ireland regarding the Galway
      mental health unit. I have not received a response within the
      statutory 20-working-day window. Please escalate to the FOI
      decision-maker.
    "#
    sender_domain "hse.ie"
    recipient_domain "cianfhoghlaim.ie"
  }
}

test ClassifyEmailMedicalCptsdTest {
  functions [ClassifyEmail]
  args {
    email_subject "CPTSD treatment pathway — second opinion request"
    email_body #"
      My GP has referred me for a second opinion on the CPTSD treatment
      pathway. Could you let me know what NHS documentation I need to
      bring to the first appointment at the Belfast clinic?
    "#
    sender_domain "nhs.uk"
    recipient_domain "gmail.com"
  }
}

test ClassifyEmailAcademicQubAdminTest {
  functions [ClassifyEmail]
  args {
    email_subject "QUB fee invoice — clarification"
    email_body #"
      I am writing to ask for clarification on the QUB tuition fee
      invoice I received last week. The line item for the PGCE
      placement fee is higher than the amount quoted in my offer
      letter. Could you confirm the correct figure?
    "#
    sender_domain "qub.ac.uk"
    recipient_domain "hotmail.com"
  }
}

test ClassifyEmailSpamTest {
  functions [ClassifyEmail]
  args {
    email_subject "WIN A FREE iPHONE NOW"
    email_body #"
      Click here to claim your prize!!! You have been selected as the
      winner of our free iPhone giveaway. Act now to claim your reward
      before this offer expires.
    "#
    sender_domain "spam-prize.example.com"
    recipient_domain "gmail.com"
  }
}
