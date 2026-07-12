// EU official languages enum.
//
// The 24 EU official language codes (ISO 639-1) that every EU
// institutional pipeline MUST restrict its `language` partition to.
//
// Irish (Gaeilge) was added as the 24th official language on
// 2022-01-01 per Council Decision (EU) 2020/2172.

enum EULanguage {
  BG  @description("Bulgarian — bg")
  HR  @description("Croatian — hr")
  CS  @description("Czech — cs")
  DA  @description("Danish — da")
  NL  @description("Dutch — nl")
  EN  @description("English — en")
  ET  @description("Estonian — et")
  FI  @description("Finnish — fi")
  FR  @description("French — fr")
  DE  @description("German — de")
  EL  @description("Greek — el")
  HU  @description("Hungarian — hu")
  GA  @description("Irish / Gaeilge — ga (added 2022)")
  IT  @description("Italian — it")
  LV  @description("Latvian — lv")
  LT  @description("Lithuanian — lt")
  MT  @description("Maltese — mt")
  PL  @description("Polish — pl")
  PT  @description("Portuguese — pt")
  RO  @description("Romanian — ro")
  SK  @description("Slovak — sk")
  SL  @description("Slovenian — sl")
  ES  @description("Spanish — es")
  SV  @description("Swedish — sv")
}
