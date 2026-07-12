// EU institutions + agencies enum.
//
// Every EU institutional pipeline MUST tag its rows with one of
// these institution slugs.

enum EUInstitution {
  EUR_LEX
    @description("eur-lex.europa.eu — the official EU law portal")
  PUBLICATIONS_OFFICE
    @description("publications.europa.eu — Publications Office of the EU")
  EURYDICE
    @description("eurydice.eacea.ec.europa.eu — the EU education information network")
  CEDEFOP
    @description("cedefop.europa.eu — European Centre for the Development of Vocational Training")
  SCHOOL_EDUCATION_GATEWAY
    @description("school-education.ec.europa.eu — School Education Gateway")
  EMA
    @description("ema.europa.eu — European Medicines Agency")
  ECDC
    @description("ecdc.europa.eu — European Centre for Disease Prevention & Control")
  EHDS
    @description("european-health-data-space.europa.eu — European Health Data Space")
  EUROSTAT
    @description("ec.europa.eu/eurostat — the EU statistical office")
  COUNCIL_OF_EUROPE
    @description("coe.int — Council of Europe (47 members, broader than the EU)")
  COE_ECHR
    @description("echr.coe.int — European Court of Human Rights")
  EUROPA_PORTAL
    @description("europa.eu — the official EU portal")
  COMMISSION_PRESS
    @description("ec.europa.eu/commission/presscorner — European Commission press releases")
  PARLIAMENT_DOCUMENTS
    @description("europarl.europa.eu — European Parliament document register")
  COUNCIL_DOCUMENTS
    @description("consilium.europa.eu — Council of the EU document register")
}
