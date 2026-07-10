// Croílár Identity Verification Schema
// Extracts non-PII metadata from identity documents (passports, vetting, registrations).
// PII documents are GPG-encrypted at rest. This schema only extracts the NON-PII summary
// that is safe to store in git and display on the public /identity page.
//
// Source: author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/identity/ + vetting/
//
// PII Handling (per croilar-portfolio spec §PII Handling):
//   - Source PDFs are GPG-encrypted with the croilar-encryption key from Infisical
//   - Only verification_metadata.json (non-PII) is committed to git
//   - Runtime decryption requires Pocket ID OIDC via the Pangolin private resource

class IdentityDocument {
  type string @description("e.g. Passport, Driving Licence, Garda Vetting, Teaching Council Registration, Birth Certificate")
  issuingAuthority string @description("e.g. Department of Foreign Affairs, National Vetting Bureau, The Teaching Council")
  documentNumber string | null @description("Last 4 digits only — full number is PII")
  issueDate string | null
  expiryDate string | null
  country string | null
  status string @description("Verified, Pending, Expired")
  verifiedBy string | null @description("Entity that verified the document")
  verifiedDate string | null
  @@stream.done
}

class GardaVetting {
  vettingReference string | null @description("Last 4 characters only")
  vettingDate string | null
  expiryDate string | null
  status string @description("Clear, Pending, Expired")
  issuingBureau string @description("e.g. National Vetting Bureau, An Garda Síochána")
  @@stream.done
}

class ProfessionalRegistration {
  registrationType string @description("e.g. Teaching Council, BCS, Engineers Ireland")
  registrationNumber string | null @description("Last 4 digits only")
  registrationDate string | null
  expiryDate string | null
  status string @description("Active, Provisional, Expired")
  subjects string[] @description("Registered subjects for teaching registrations")
  @@stream.done
}

class VerificationSummary {
  documents IdentityDocument[]
  vetting GardaVetting | null
  registrations ProfessionalRegistration[]
  totalVerified int
  totalPending int
  totalExpired int
  lastUpdated string
}

function ExtractIdentityDocument(text: string) -> IdentityDocument[] {
  // Extracts non-PII identity document metadata.
  // PASS/FAIL only — do NOT extract full document numbers, names, addresses, or birth dates.
  // Redact all PII fields to last 4 digits or omit.
}

function ExtractGardaVetting(text: string) -> GardaVetting[] {
  // Extracts Garda Vetting metadata.
  // Reference number last 4 digits only. Status: Clear / Pending / Expired.
}

function ExtractProfessionalRegistration(text: string) -> ProfessionalRegistration[] {
  // Extracts professional registration metadata.
  // Teaching Council, BCS, etc. Registration number last 4 digits only.
}

function GenerateVerificationSummary(docs: IdentityDocument[], vetting: GardaVetting[], regs: ProfessionalRegistration[]) -> VerificationSummary {
  // Aggregates all verification data into a single summary.
  // Counts verified, pending, and expired documents.
  // Sets lastUpdated to the current date.
}
