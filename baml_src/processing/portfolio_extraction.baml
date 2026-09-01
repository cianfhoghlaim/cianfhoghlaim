// === ARCHIVED 2026-06-24 ===
// The 6 functions in this file (ExtractProfileFromCV
// ExtractGameProject, MergeProfiles, GenerateProfileSummary)
// have no current Python consumer in the oideachais quadrant.
// They are intended for the croilar/ portfolio surface (per
// `croilar/AGENTS.md`), which is not yet built for persona
// profiles beyond the existing static pages.
//
// To re-activate:
// 1. Implement the consumer (e.g.
//    croilar/dagster_assets/profile_extraction.py OR
//    meaisinfhoghlaim/agents/croilar_cv_extraction.py)
// 2. Move this file back to baml_src/ (git mv)
// 3. Remove the ARCHIVED header from the top
// 4. Update STATUS.md to mark the functions as wired
// 5. Update REFACTORING.md to remove the archive entry
//
// Reference: openspec/changes/archive-celtic-baml-orphans/
// =====================================================================

// =============================================================================
// PORTFOLIO EXTRACTION SCHEMA
// =============================================================================
// BAML schemas for extracting profile data from various sources:
// - CV/Resume documents
// - GitHub profiles and READMEs
// - Spotify/SoundCloud artist data
// - LinkedIn profiles
// - Personal websites
//
// Used by multi-tenant portfolio system for cianfhoghlaim.ie and aleyum.com
// =============================================================================

// =============================================================================
// ENUMS
// =============================================================================

enum ProfileType {
    DEVELOPER @description("Software developer/engineer profile")
    MUSICIAN @description("Music producer/artist profile")
    EDUCATOR @description("Educator/teacher profile")
    RESEARCHER @description("Academic/researcher profile")
    HYBRID @description("Multi-disciplinary profile")
}

enum PortfolioSkillCategory {
    PROGRAMMING_LANGUAGE @description("Programming languages like Python, TypeScript, Rust")
    FRAMEWORK @description("Frameworks like React, FastAPI, TanStack")
    DATABASE @description("Database technologies like PostgreSQL, DuckDB")
    DEVOPS @description("DevOps tools like Docker, Kubernetes, CI/CD")
    CLOUD @description("Cloud platforms like AWS, GCP, Cloudflare")
    AI_ML @description("AI/ML technologies like PyTorch, LangChain")
    GAME_ENGINE @description("Game engines like Unity, Unreal, Godot")
    AUDIO @description("Audio production tools like Ableton, Logic Pro")
    DESIGN @description("Design tools like Figma, Adobe Suite")
    LANGUAGE @description("Natural languages (human languages)")
    OTHER @description("Other skills not fitting above categories")
}

enum ProjectStatus {
    ACTIVE @description("Currently being developed")
    COMPLETED @description("Finished project")
    ARCHIVED @description("No longer maintained")
    CONCEPT @description("Planning/concept stage")
}

enum MusicGenrePortfolio {
    ELECTRONIC @description("Electronic music including EDM, house, techno")
    AMBIENT @description("Ambient and atmospheric music")
    EXPERIMENTAL @description("Experimental and avant-garde")
    INDIE @description("Indie music")
    SOUNDTRACK @description("Film/game soundtracks")
    CELTIC @description("Celtic traditional or Celtic fusion")
    OTHER @description("Other genres")
}

enum PlatformType {
    GITHUB @description("GitHub repository or profile")
    SPOTIFY @description("Spotify artist or playlist")
    SOUNDCLOUD @description("SoundCloud profile or tracks")
    YOUTUBE @description("YouTube channel or videos")
    LINKEDIN @description("LinkedIn profile")
    PERSONAL_WEBSITE @description("Personal portfolio website")
    TWITTER @description("Twitter/X profile")
    OTHER @description("Other platforms")
}

// =============================================================================
// CORE TYPES
// =============================================================================

// Contact information
class ContactInfo {
    email string? @description("Primary email address")
    phone string? @description("Phone number")
    location string? @description("City, Country or general location")
    website string? @description("Personal website URL")
    linkedin string? @description("LinkedIn profile URL or username")
    github string? @description("GitHub username or profile URL")
    twitter string? @description("Twitter/X handle")
}

// Technical skill with proficiency level
class PortfolioSkill {
    name string @description("PortfolioSkill name, e.g., 'Python', 'React', 'Docker'")
    category PortfolioSkillCategory @description("Category of the skill")
    proficiency int? @description("Proficiency level 1-5 (1=beginner, 5=expert)")
    yearsExperience int? @description("Years of experience with this skill")
    keywords string[] @description("Related keywords or sub-skills")
}

// Work experience entry
class Experience {
    company string @description("Company or organization name")
    title string @description("Job title or role")
    location string? @description("Location of the role")
    startDate string? @description("Start date (YYYY-MM format)")
    endDate string? @description("End date (YYYY-MM format, null if current)")
    isCurrent bool @description("Whether this is the current role")
    description string @description("Description of responsibilities and achievements")
    highlights string[] @description("Key achievements or highlights")
    technologies string[] @description("Technologies used in this role")
}

// Education entry
class Education {
    institution string @description("University, college, or school name")
    degree string @description("Degree type (e.g., BSc, MSc, PhD)")
    field string @description("Field of study")
    location string? @description("Location of institution")
    startDate string? @description("Start date (YYYY format)")
    endDate string? @description("End date (YYYY format)")
    grade string? @description("Grade/GPA/classification if available")
    description string? @description("Additional details about the education")
}

// Project entry
class Project {
    name string @description("Project name")
    description string @description("Project description")
    status ProjectStatus @description("Current status of the project")
    url string? @description("URL to project (repo, demo, etc.)")
    technologies string[] @description("Technologies used")
    highlights string[] @description("Key features or achievements")
    startDate string? @description("When the project started")
    endDate string? @description("When the project ended (null if ongoing)")
    role string? @description("Your role in the project")
    category string? @description("Category like 'web', 'game', 'ai', 'data'")
}

// Social/platform link
class SocialLink {
    platform PlatformType @description("Platform type")
    url string @description("Full URL to the profile")
    username string? @description("Username on the platform")
    followers int? @description("Number of followers if available")
}

// =============================================================================
// MUSIC-SPECIFIC TYPES (for aleyum.com)
// =============================================================================

// Music track or release
class MusicTrack {
    title string @description("Track title")
    artist string @description("Artist name (could be alias)")
    album string? @description("Album name if part of an album")
    releaseDate string? @description("Release date (YYYY-MM-DD)")
    duration int? @description("Duration in seconds")
    genres MusicGenrePortfolio[] @description("Genres of the track")
    streamingUrls map<string, string> @description("Map of platform to URL")
    playCount int? @description("Total play count across platforms")
    isOriginal bool @description("Whether this is an original composition")
}

// Music album or EP
class MusicRelease {
    title string @description("Album/EP title")
    artist string @description("Artist name")
    releaseDate string? @description("Release date")
    tracks MusicTrack[] @description("Tracks in the release")
    artwork string? @description("Cover artwork URL")
    label string? @description("Record label if any")
    type string @description("Album, EP, Single, etc.")
}

// Music profile data from streaming platforms
class MusicProfile {
    artistName string @description("Main artist/producer name")
    aliases string[] @description("Other names/aliases used")
    bio string? @description("Artist biography")
    genres MusicGenrePortfolio[] @description("Primary genres")
    monthlyListeners int? @description("Monthly listeners (Spotify)")
    followers int? @description("Total followers across platforms")
    releases MusicRelease[] @description("Discography")
    topTracks MusicTrack[] @description("Top/popular tracks")
    collaborators string[] @description("Frequent collaborators")
    equipment string[] @description("Production equipment/software")
    influences string[] @description("Musical influences")
}

// =============================================================================
// GAME DEV SPECIFIC TYPES (for aleyum.com game showcase)
// =============================================================================

// Game engine/technology
class GameTechnology {
    name string @description("Technology name like 'Unity', 'Unreal', 'Godot'")
    category string @description("Category like 'engine', 'shader', 'networking'")
    proficiency int? @description("Proficiency level 1-5")
    projects string[] @description("Projects using this technology")
}

// Game project
class GameProject {
    title string @description("Game/project title")
    description string @description("Project description")
    engine string @description("Game engine used")
    platforms string[] @description("Target platforms")
    technologies string[] @description("Other technologies used")
    role string @description("Your role (e.g., 'Lead Developer', 'Sound Designer')")
    status ProjectStatus @description("Project status")
    demoUrl string? @description("Playable demo URL")
    repoUrl string? @description("Source code repository")
    mediaUrls string[] @description("Screenshots, videos, etc.")
    releaseDate string? @description("Release date if published")
}

// =============================================================================
// COMPLETE PROFILE TYPES
// =============================================================================

// Developer-focused profile
class DeveloperProfile {
    name string @description("Full name")
    title string @description("Professional title")
    summary string @description("Professional summary/bio")
    contact ContactInfo @description("Contact information")
    skills PortfolioSkill[] @description("Technical skills")
    experience Experience[] @description("Work experience")
    education Education[] @description("Education history")
    projects Project[] @description("Notable projects")
    certifications string[] @description("Professional certifications")
    publications string[] @description("Papers, articles, blog posts")
    socialLinks SocialLink[] @description("Social media/platform links")
    languages string[] @description("Natural languages spoken")
}

// Music producer profile
class MusicProducerProfile {
    name string @description("Real name")
    stageName string @description("Stage/artist name")
    title string @description("e.g., 'Music Producer & Sound Designer'")
    bio string @description("Artist biography")
    contact ContactInfo @description("Contact information")
    musicProfile MusicProfile @description("Music-specific data")
    technicalSkills PortfolioSkill[] @description("Audio/technical skills")
    gameAudio GameProject[] @description("Game audio projects if any")
    socialLinks SocialLink[] @description("Platform links")
}

// Combined/hybrid profile (for aleyum.com type portfolios)
class HybridProfile {
    name string @description("Full name")
    primaryName string @description("Name to display (could be stage name)")
    title string @description("Combined professional title")
    summary string @description("Overall professional summary")
    contact ContactInfo @description("Contact information")
    profileType ProfileType @description("Primary profile type")

    // Developer aspects
    technicalSkills PortfolioSkill[] @description("Technical/programming skills")
    projects Project[] @description("Software projects")
    experience Experience[] @description("Work experience")
    education Education[] @description("Education")

    // Creative aspects
    musicProfile MusicProfile? @description("Music profile if applicable")
    gameProjects GameProject[] @description("Game development projects")
    creativeWorks Project[] @description("Other creative works")

    socialLinks SocialLink[] @description("All social/platform links")
    languages string[] @description("Languages spoken")
}

// =============================================================================
// EXTRACTION FUNCTIONS
// =============================================================================

// Extract profile from CV/resume document
function ExtractProfileFromCV(
  document: string
) -> HybridProfile {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

// Extract profile from GitHub README
function ExtractProfileFromGitHubReadme(
  readme: string,
  username: string
) -> DeveloperProfile {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

// Extract music profile from Spotify/SoundCloud data
function ExtractMusicProfile(
  platformData: string,
  platform: PlatformType
) -> MusicProfile {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

// Extract game project details from documentation/README
function ExtractGameProject(
  projectDocs: string
) -> GameProject {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

// Merge profiles from multiple sources into unified profile
function MergeProfiles(
  profiles: HybridProfile[]
) -> HybridProfile {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

// Generate profile summary for a specific tenant context
function GenerateProfileSummary(
  profile: HybridProfile,
  tenantType: ProfileType,
  maxLength: int
) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

// =============================================================================
// TESTS
// =============================================================================

// test ExtractProfileFromCVTest {
//     functions [ExtractProfileFromCV]
//     args {
//         document #"
//             CONOR HYNES
//             Music Producer & Game Developer
//             Dublin, Ireland
//             conor@aleyum.com | github.com/aleyum | spotify.com/artist/aleyum
// 
//             SUMMARY
//             Electronic music producer and game developer with 5+ years experience
//             creating ambient soundscapes and interactive audio experiences.
// 
//             SKILLS
//             - Audio: Ableton Live, Logic Pro X, Max/MSP
//             - Game Dev: Unity, Unreal Engine 5, FMOD
//             - Programming: C#, Python, TypeScript
// 
//             EXPERIENCE
//             Freelance Music Producer | 2019 - Present
//             - Released 3 EPs on indie labels
//             - Composed soundtracks for 5 indie games
// 
//             EDUCATION
//             BA Music Technology | Trinity College Dublin | 2019
//         "#
//     }
// }

// test ExtractMusicProfileTest {
//     functions [ExtractMusicProfile]
//     args {
//         platformData #"
//             Artist: Aleyum
//             Monthly Listeners: 15,432
//             Genres: Electronic, Ambient, Experimental
// 
//             Top Tracks:
//             1. Connemara Dreams - 45,000 plays
//             2. Celtic Circuits - 32,000 plays
//             3. Digital Fog - 28,000 plays
// 
//             Albums:
//             - "Spectral Waves" EP (2024) - 6 tracks
//             - "Memory Palace" (2023) - 10 tracks
//         "#
//         platform PlatformType.SPOTIFY
//     }
// }
