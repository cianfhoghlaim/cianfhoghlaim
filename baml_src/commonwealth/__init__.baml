// Commonwealth of Nations BAML cluster — re-exports.

class CommonwealthMemberState {
  ISO3 string @description("ISO 3166-1 alpha-3 (lowercase) — e.g. aus, can, nzl, ind, zaf")
  NAME string @description("The English-language country name")
  REGION string @description("Commonwealth region — africa | asia | caribbean | europe | pacific | americas")
}
