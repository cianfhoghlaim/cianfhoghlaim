// BAML schema: Gaeilge Quest Pack Generator (LC + JC)
//
// Builds formative assessment quest packs for NCCA Leaving Certificate
// Gaeilge (Irish) — taught IN IRISH. Bilingual EN+GA is special here:
// `text_en` is typically null for content; `text_ga` is the canonical
// value. The `text_en` field is reserved for citation + helper
// translation only.
//
// Gaeilge is the only subject taught primarily in Irish at the LC.
// 3 NCCA levels: Foundation, Ordinary, Higher.
//
// Topics: Léamhthuiscint, Litríocht, Gramadach, Filíocht, Prós,
// Béaloideas, Scríbhneoireacht (composition), Cluastuiscint
// (listening comprehension).
//
// Usage:
//   pack = b.GenerateGaelQuestPack(syllabus, past_papers, marking_schemes, "hl")
//   item = b.GenerateGaelFormativeItem("LC-GAEL-LO-2.4", difficulty=3)
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

enum GaelNCCALevel {
  LC_FL @description("Leaving Certificate Foundation Level Gaeilge")
  LC_OL @description("Leaving Certificate Ordinary Level Gaeilge")
  LC_HL @description("Leaving Certificate Higher Level Gaeilge")
  JC    @description("Junior Cycle Gaeilge")
}

enum GaelTopicArea {
  LEAMHTHUISCINT     @description("Reading comprehension (aistí, nuachtlitirí, filíocht)")
  LITRIOCHT          @description("Literature: prós + filíocht + drámaíocht")
  GRAMADACH          @description("Grammar: aimsirí, modhanna, réimíreanna, tuiseal")
  FILIOCHT           @description("Poetry: filí móra (Ó Rathaille, Mhac an tSaoi, Ní Dhomhnaill)")
  PROS               @description("Prose: úrscéal, gearrscéal, aistí")
  BEALOIDEAS         @description("Folk tradition: scéalta, laethanta saint, paimsire")
  SCRIBHNEOIREACHT   @description("Composition: aistí, scéalta, litreacha, tráchtas")
  CLUASTUISCINT      @description("Listening comprehension (aural exam component)")
  SCOLAI             @description("Scholarly analysis of prescribed texts")
  CUNTASAIOCHT       @description("Translation EN ↔ GA")
}

enum GaelItemType {
  LEAMHTHUISCINT_ITEM   @description("Reading comprehension item")
  GRAMADACH_ITEM         @description("Grammar transformation / fill-in-the-blank")
  AISTRIUCHAN_ITEM        @description("Translation EN ↔ GA")
  COMHRA_ITEM            @description("Conversation / dialogue")
  FILIOCHT_ANALYSIS     @description("Poetry analysis")
  LITRIOCHT_ANALYSIS    @description("Prose / drama analysis")
  COMPOSITION_PROMPT    @description("Long-form composition prompt")
  CLUASTUISCINT_ITEM     @description("Listening comprehension (transcribed audio)")
}

enum GaelFeedbackChannel {
  GAEL_TUTOR            @description("Gaeilge-medium feedback (native tutor)")
  QUEST_GUIDE           @description("Graduated hints (4 levels)")
  CURRICULUM_LOOKUP     @description("Direct NCCA LO citation")
  GRAMADACH_REVIEW      @description("Grammar review + conjugation tables")
  RESEARCH_ASSISTANT    @description("Cross-subject synthesis")
}

class GaelBilingualText {
  text_en string? @description("English translation; null for Irish-only Gaeilge content")
  text_ga string  @description("Canonical Irish text (required)")
}

class GaelEvidenceLink {
  source_pdf string
  source_page int @description("PDF page (1-indexed)")
  excerpt_ga string  @description("Verbatim Irish excerpt (canonical)")
  excerpt_en string? @description("Optional English translation")
  ncca_url string?
}

class GaelNCCALearningOutcome {
  lo_code string @description("Canonical NCCA code, e.g. 'LC-GAEL-LO-3.1'")
  framework string @description("'ncca-lc' or 'ncaa-jc'")
  level GaelNCCALevel
  topic GaelTopicArea
  competency_text GaelBilingualText @description("NCCA competency statement (Irish canonical)")
  marking_scheme_excerpt GaelBilingualText?
  evidence GaelEvidenceLink
}

class GaelFormativeItem {
  id string
  lo_code string
  level GaelNCCALevel
  topic GaelTopicArea
  item_type GaelItemType
  difficulty int @description("1-5")
  prompt GaelBilingualText @description("Irish canonical; English null for comprehension items")
  expected_answer GaelBilingualText
  marking_scheme GaelBilingualText
  common_errors GaelBilingualText[]
  hints GaelBilingualText[] @description("4 graduated hints (Irish canonical)")
  evidence GaelEvidenceLink
  feedback_channel GaelFeedbackChannel
  est_time_minutes int @description("1-30")
}

class GaelFormativeItemAttempt {
  item_id string
  student_response string @description("Student's response (Irish expected)")
  response_format string @description("text / latex / image / audio")
  time_taken_seconds int
  hints_used int @description("0-4")
}

class GaelScoreBreakdown {
  item_id string
  lo_code string
  total_marks int
  marks_awarded int
  marks_per_step int[]
  is_correct bool
  partial_credit_pct float @description("0-100")
  feedback_ga string  @description("Irish feedback (canonical)")
  feedback_en string? @description("Optional English translation of feedback")
  next_recommended_lo string?
  badge_earned bool @description("True iff partial_credit_pct >= 80")
}

class GaelQuestPack {
  id string
  subject string @description("Always 'gaeilge'") @stream.not_null
  framework string @description("'ncca-lc' or 'ncca-jc'")
  level GaelNCCALevel
  title GaelBilingualText @stream.not_null
  description GaelBilingualText
  total_items int
  total_marks int
  est_time_minutes int
  los_covered string[]
  items GaelFormativeItem[] @stream.with_state
  prerequisites string[]
  cross_subject_links string[] @description("LC-ENGL, LC-HIST for cross-language synthesis")
  generated_at string
  generated_by string @description("Always 'gael_agent'")
}

class GaelQuestPackValidation {
  pack_id string
  is_valid bool
  errors string[]
  warnings string[]
}

// ============================================================================
// Real generation prompts (2026-08-08 docs-informed-quest-and-credential-
// generation-v1 change). Grounded in the v3 extraction types. `level: JC`
// is Junior Cycle Gaeilge — no separate file. Gaeilge content is Irish-
// medium: text_ga is always required and canonical; text_en is null for
// content fields (only used for citation/helper translation), matching the
// existing GaelBilingualText nullability.
// ============================================================================

function GenerateGaelQuestPack(
  syllabus: SyllabusDocument,
  past_papers: ExamPaper[],
  marking_schemes: MarkingScheme[],
  level: string
) -> GaelQuestPack {  client ExtractEn
  prompt #"
    Tá tú ag tógáil pacáiste ceartúcháin fhoirmitheach Gaeilge do mhic léinn
    NCCA ag leibhéal {{ level }} ("JC" = Sraith Shóisearach; "LC_FL"/"LC_OL"/
    "LC_HL" = Ardteistiméireacht Bhonn/Ghnáth/Ard). Bunaigh gach mír ar an
    siollabas oifigiúil, ar na scrúdpháipéir a chuaigh thart, agus ar an
    treoir maidir leis an scéim mharcála thíos — ná cum ábhar nach bhfuil sa
    téacs bunaidh.

    Siollabas oifigiúil:
    {{ syllabus }}

    Scrúdpháipéir a chuaigh thart:
    {{ past_papers }}

    Treoir maidir leis an scéim mharcála:
    {{ marking_schemes }}

    Tóg GaelQuestPack:
    - subject: "gaeilge"
    - framework: "ncca-lc" má thosaíonn level le "LC", "ncca-jc" más "JC" é
    - level: an GaelNCCALevel a fhreagraíonn do {{ level }}
    - title / description: text_ga i gcónaí, text_en null (ní hé Béarla an
      teanga theagaisc)
    - items: mír amháin GaelFormativeItem do gach toradh foghlama atá i
      láthair go hiarbhír in syllabus.module_topics[].learning_outcomes —
      prompt/expected_answer/marking_scheme bunaithe ar théacs iarbhír an
      tsiollabais; nuair a mheaitseálann related_lo_id ceist ó pháipéar a
      chuaigh thart, cuir a stíl agus a leithdháileadh marcanna san áireamh;
      leideanna ag méadú ó leid éadrom go freagra beagnach iomlán; tá
      evidence.source_page agus evidence.excerpt_ga (móide excerpt_en más
      ann dó) cóipeáilte go litriúil ón téacs bunaidh, ná cum riamh iad;
      evidence.source_pdf ó syllabus.source_pdf
    - los_covered: gach toradh foghlama atá sa siollabas iarbhír
    - total_items / total_marks / est_time_minutes: suimeanna ó na míreanna iarbhír
    - prerequisites / cross_subject_links: an méid a luann réimse
      cross_curricular nó assessment_objectives an tsiollabais amháin
    - generated_at: dáta-am ISO-8601 reatha
    - generated_by: "gael_agent"

    Áirigh agus luaigh go cúramach ón téacs iarbhír. Aschur díreach amháin
    réad JSON iomlán a fhreagraíonn do GaelQuestPack. Ná húsáid ellipses
    (...) ná nótaí; cuir gach mír san áireamh ina hiomláine.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ExtractGaelLOStatement(paragraph: string) -> string[] {  client ExtractEn
  prompt #"
    Bain amach gach ráiteas toraidh foghlama Gaeilge NCCA ar leith ón
    mhír shiollabais thíos. Cuir gach ceann ar ais mar théad ar leith, go
    litriúil ón téacs — ná cumaisc ilthorthaí i dtéad amháin.

    {{ _.role("user") }}
    Mír:
    {{ paragraph }}

    {{ ctx.output_format }}
  "#
}

// -----------------------------------------------------------------------------
// ExtractGaelGaStatement (added 2026-07-13-baml-cocoindex-tutorials-ga-v1)
// -----------------------------------------------------------------------------
// The bilingual EN+GA variant of ExtractGaelLOStatement. Identical
// shape (`string[]`) but the prompt is Irish-first and routes via
// `client Default` so it can be benchmarked against the EN variant
// (`ExtractGaelLOStatement` → `client ExtractEn`). Both shapes
// emit the same list-of-strings shape so the qpack pipeline can
// run either path without code changes.

function ExtractGaelGaStatement(paragraph: string) -> string[] {  client ExtractEn
  prompt #"
    Bain amach gach ráiteas toraidh foghlama Gaeilge ar leith ón mhír
    shiollabais thíos, go litriúil. Seo an leagan Gaeilge-tosaithe den
    aisghabhálaí céanna — filleann sé an chéanna liosta téad más féidir,
    ach tugann tosaíocht don leagan Gaeilge nuair a bhíonn dhá leagan ann.

    {{ _.role("user") }}
    Mír:
    {{ paragraph }}

    {{ ctx.output_format }}
  "#
}

function GenerateGaelFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  evidence: GaelEvidenceLink
) -> GaelFormativeItem {  client ExtractEn
  prompt #"
    Tá tú ag scríobh mír aonair measúnaithe fhoirmithigh do thoradh foghlama
    Gaeilge NCCA {{ lo_code }} (ábhar: {{ topic }}, leibhéal: {{ level }},
    deacracht sprioctha: {{ difficulty }}/5).

    Bunaigh an mhír go hiomlán ar an fhianaise litriúil seo ón siollabas
    oifigiúil — ná scríobh ceist ghinearálta Gaeilge nach mbaineann léi:

    {{ evidence }}

    Tóg GaelFormativeItem:
    - id: UUID nua
    - lo_code: {{ lo_code }}, level: an GaelNCCALevel a fhreagraíonn do
      {{ level }}, topic: an GaelTopicArea a fhreagraíonn do {{ topic }}
    - item_type: roghnaigh an cineál is fearr a oireann don fhianaise (m.sh.
      LEAMHTHUISCINT_ITEM do léamhthuiscint, GRAMADACH_ITEM do ghramadach,
      FILIOCHT_ANALYSIS d'anailís fhilíochta)
    - difficulty: {{ difficulty }}
    - prompt / expected_answer / marking_scheme: text_ga i gcónaí, bunaithe
      ar shliocht na fianaise, ní teimpléad ginearálta
    - common_errors: earráidí dóchúla don toradh sonrach seo
    - hints: 4 go díreach, ag méadú ó leid éadrom go freagra beagnach iomlán
    - evidence: cuir an fhianaise ionchuir ar aghaidh gan athrú
    - feedback_channel: GAEL_TUTOR d'aiseolas ábhair, GRAMADACH_REVIEW do
      mhíreanna gramadaí
    - est_time_minutes: réalaíoch don deacracht (1-30)

    Aschur díreach amháin réad JSON iomlán a fhreagraíonn do GaelFormativeItem.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ScoreGaelFormativeResponse(
  item: GaelFormativeItem,
  attempt: GaelFormativeItemAttempt
) -> GaelScoreBreakdown {  client ExtractEn
  prompt #"
    Tá tú ag marcáil freagra mic léinn ar mhír fhoirmitheach Gaeilge, ag
    baint úsáide as scéim mharcála na míre féin.

    Mír (lena n-áirítear expected_answer agus marking_scheme):
    {{ item }}

    Iarracht an mhic léinn:
    {{ attempt }}

    Tóg GaelScoreBreakdown:
    - item_id: {{ item.id }}, lo_code: {{ item.lo_code }}
    - total_marks: díorthaithe ó leithdháileadh scéim mharcála na míre
    - marks_awarded / marks_per_step: creidmheas páirteach de réir na scéime
    - is_correct: fíor más ionann marks_awarded agus total_marks
    - partial_credit_pct: marks_awarded / total_marks * 100
    - feedback_ga: aiseolas sonrach, i nGaeilge i gcónaí; feedback_en: roghnach
    - next_recommended_lo: an chéad toradh eile is dóchúil, más ábhartha
    - badge_earned: fíor más >= 80 é partial_credit_pct

    Aschur díreach amháin réad JSON iomlán a fhreagraíonn do GaelScoreBreakdown.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ValidateGaelQuestPack(pack: GaelQuestPack) -> GaelQuestPackValidation {  client ExtractEn
  prompt #"
    Deimhnigh comhsheasmhacht inmheánach an GaelQuestPack seo — ba chóir go
    mbeadh lo_code gach míre in los_covered, total_items comhionann le
    items.length, total_marks comhionann le suim leithdháileadh gach míre,
    agus gan aon mhír le evidence.excerpt_ga folamh.

    Pacáiste ceistiúcháin:
    {{ pack }}

    Tóg GaelQuestPackValidation: pack_id ón ionchur, is_valid fíor mura
    bhfuarthas aon earráid, errors do neamhréireachtaí crua, warnings do
    aon rud amhrasach ach ceart go leor.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}